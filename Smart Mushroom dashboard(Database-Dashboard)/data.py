"""
Shared real data for the Smart Mushroom Farm dashboard.

This replaces the mock lists that used to live here. Every function has
the SAME name and returns the SAME shape (list of dicts / dict) as
before, so Home.py, 1_Live_Monitoring.py, and the other pages don't
need to change how they call these — only what happens inside them
changed.

A "room" is the physical space with one door and one set of fans/
humidifier. A "rack" is a shelf inside that room — each rack has its
own sensors (temperature, humidity, CO2, light, substrate moisture),
but door events, power events, and actuator state belong to the ROOM,
since every rack in that room shares the same door and same fans.
"""

from datetime import datetime, timedelta
from db import get_connection

# Target ranges — used to decide "ok" vs "warn" for a rack, and shared
# with Graphs/Settings so that means the same thing everywhere.
TARGETS = {
    "temperature": (20.0, 24.0),
    "humidity": (85.0, 95.0),
    "co2": (0.0, 800.0),
    "light": (200.0, 500.0),
    "substrate_moisture": (55.0, 70.0),
}

OFFLINE_AFTER_MINUTES = 15  # a rack with no reading in this long shows "offline"


def _time_ago(dt):
    """Turns a datetime into a friendly string like '3 min ago'."""
    if dt is None:
        return "no data"
    delta = datetime.now() - dt
    minutes = int(delta.total_seconds() // 60)
    if minutes < 1:
        return "just now"
    if minutes < 60:
        return f"{minutes} min ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hr ago"
    return f"{hours // 24} day(s) ago"


def latest_reading(cursor, rack_id, sensor_type):
    """Most recent value for one sensor_type on one rack.
    Returns (value, recorded_at) or (None, None) if there's no data yet."""
    cursor.execute(
        """SELECT sr.sensor_value, sr.recorded_at
           FROM sensor_readings sr
           JOIN sensors s ON s.sensor_id = sr.sensor_id
           WHERE s.rack_id = %s AND s.sensor_type = %s
           ORDER BY sr.recorded_at DESC LIMIT 1""",
        (rack_id, sensor_type),
    )
    row = cursor.fetchone()
    if not row:
        return None, None
    return float(row["sensor_value"]), row["recorded_at"]


def _compute_status(readings, latest_time):
    if latest_time is None or (datetime.now() - latest_time) > timedelta(minutes=OFFLINE_AFTER_MINUTES):
        return "offline"
    for var, (lo, hi) in TARGETS.items():
        val = readings.get(var)
        if val is not None and not (lo <= val <= hi):
            return "warn"
    return "ok"


def get_rooms():
    """The physical rooms, each with its door-event count, power-event
    count (last 24h), and current actuator states."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT room_id, room_code FROM rooms")
    rooms = cur.fetchall()

    for room in rooms:
        cur.execute(
            """SELECT COUNT(*) AS c FROM door_events
               WHERE room_id = %s AND occurred_at >= NOW() - INTERVAL 24 HOUR""",
            (room["room_id"],),
        )
        room["door_events_24h"] = cur.fetchone()["c"]

        cur.execute(
            """SELECT COUNT(*) AS c FROM power_consumption
               WHERE room_id = %s AND start_time >= NOW() - INTERVAL 24 HOUR""",
            (room["room_id"],),
        )
        room["power_interruptions_24h"] = cur.fetchone()["c"]

        # Latest state per actuator name in this room (requires the
        # room_id column added by actuator_room_id_migration.sql)
        cur.execute(
            """SELECT a1.actuator_name, a1.state
               FROM actuator_status_log a1
               INNER JOIN (
                   SELECT actuator_name, MAX(updated_at) AS max_time
                   FROM actuator_status_log
                   WHERE room_id = %s
                   GROUP BY actuator_name
               ) latest ON a1.actuator_name = latest.actuator_name
                        AND a1.updated_at = latest.max_time
               WHERE a1.room_id = %s""",
            (room["room_id"], room["room_id"]),
        )
        room["actuators"] = cur.fetchall()

    cur.close()
    conn.close()
    return rooms


def get_room(room_id):
    return next(r for r in get_rooms() if r["room_id"] == room_id)


def get_room_events(room_id):
    """Door events, power events, and actuator state for one room."""
    return get_room(room_id)


def get_racks():
    """Every rack with its latest environmental readings, computed
    status (ok/warn/offline), and which room it belongs to."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        """SELECT r.rack_id, r.room_id, r.rack_code, rm.room_code,
                  (SELECT b.batch_id FROM batches b
                   WHERE b.rack_id = r.rack_id AND b.status = 'active'
                   ORDER BY b.inoculation_date DESC LIMIT 1) AS batch_id
           FROM racks r
           JOIN rooms rm ON rm.room_id = r.room_id"""
    )
    racks_raw = cur.fetchall()

    variables = ["temperature", "humidity", "co2", "light", "substrate_moisture"]
    result = []
    for rack in racks_raw:
        readings = {}
        latest_time = None
        for var in variables:
            value, recorded_at = latest_reading(cur, rack["rack_id"], var)
            readings[var] = value
            if recorded_at and (latest_time is None or recorded_at > latest_time):
                latest_time = recorded_at

        status = _compute_status(readings, latest_time)

        result.append({
            "rack_id": rack["rack_id"],
            "room_id": rack["room_id"],
            "rack_code": rack["rack_code"],
            "room_code": rack["room_code"],
            "display_name": f"{rack['room_code']} \u00b7 {rack['rack_code']}",
            "status": status,
            "batch_id": rack["batch_id"],
            "last_update": _time_ago(latest_time),
            **readings,
        })

    cur.close()
    conn.close()
    return result


def average_conditions(racks):
    """Farm-wide average per variable across all reporting (non-offline)
    racks. Pure Python — no DB access, works the same as before."""
    reporting = [r for r in racks if r["status"] != "offline"]
    variables = ["temperature", "humidity", "co2", "light", "substrate_moisture"]
    result = {}
    for var in variables:
        values = [r[var] for r in reporting if r.get(var) is not None]
        if not values:
            result[var] = {"value": None, "status": "offline"}
            continue
        avg = round(sum(values) / len(values), 1)
        lo, hi = TARGETS[var]
        status = "ok" if lo <= avg <= hi else "warn"
        result[var] = {"value": avg, "status": status}
    return result, len(reporting), len(racks)


def get_system_health():
    """Real sensor count (total registered vs. reported recently), plus
    the timestamp of the most recent reading from any sensor. ESP32 and
    Raspberry Pi connection status stay as simple placeholders for now
    since there's no separate heartbeat table tracking those devices yet."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) AS c FROM sensors")
    total = cur.fetchone()["c"]

    cur.execute(
        """SELECT COUNT(DISTINCT sr.sensor_id) AS c
           FROM sensor_readings sr
           WHERE sr.recorded_at >= NOW() - INTERVAL %s MINUTE""",
        (OFFLINE_AFTER_MINUTES,),
    )
    online = cur.fetchone()["c"]

    cur.execute("SELECT MAX(recorded_at) AS latest FROM sensor_readings")
    latest = cur.fetchone()["latest"]

    cur.close()
    conn.close()

    return {
        "sensors_online": online,
        "sensors_total": total,
        "esp32": "ok",
        "raspberry_pi": "ok",
        "last_sync": _time_ago(latest),
    }
