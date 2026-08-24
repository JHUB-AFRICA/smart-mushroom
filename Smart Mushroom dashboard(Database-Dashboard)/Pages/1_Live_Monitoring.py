"""
Smart Mushroom Farm — Live Monitoring
Room/rack readings, actuator status, and camera snapshots.

Reads from the real MySQL schema (sensors, sensor_readings,
actuator_status_log, images tables) via db.get_connection() and
data.latest_reading().
"""

import streamlit as st
from theme import inject_css, page_header, status_class, badge_class, card_open, card_close
from data import get_racks, get_room_events, latest_reading, _time_ago
from db import get_connection

st.set_page_config(page_title="Live Monitoring · Smart Mushroom Farm", page_icon="🍄", layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────────────────────
# get_racks()/get_room_events() live in data.py. Door events and
# actuators come from the ROOM (shared by every rack inside it, since
# racks in the same room share one door and one set of fans/humidifier).
# Substrate temp and ACH stay per-rack since each shelf has its own probe.
# ─────────────────────────────────────────────────────────────

def get_rack_detail(rack_id):
    """substrate_temp + ACH sensor readings, plus the active batch's
    current phenology stage, for one rack."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    substrate_temp, _ = latest_reading(cur, rack_id, "substrate_temp")
    ach, _ = latest_reading(cur, rack_id, "ach")

    cur.execute(
        """SELECT batch_id, batch_code FROM batches
           WHERE rack_id = %s AND status = 'active'
           ORDER BY inoculation_date DESC LIMIT 1""",
        (rack_id,),
    )
    batch = cur.fetchone()

    stage = "unknown"
    if batch:
        cur.execute(
            """SELECT stage FROM phenology_events
               WHERE batch_id = %s ORDER BY event_date DESC LIMIT 1""",
            (batch["batch_id"],),
        )
        row = cur.fetchone()
        if row:
            stage = row["stage"]

    cur.close()
    conn.close()
    return {
        "substrate_temp": substrate_temp,
        "ach": ach,
        "batch_code": batch["batch_code"] if batch else "—",
        "stage": stage,
    }

def get_latest_snapshot(rack_id):
    """Most recent photo for this rack's active batch."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """SELECT i.captured_at, i.stage_tag
           FROM images i
           WHERE i.batch_id = (
               SELECT batch_id FROM batches
               WHERE rack_id = %s AND status = 'active'
               ORDER BY inoculation_date DESC LIMIT 1
           )
           ORDER BY i.captured_at DESC LIMIT 1""",
        (rack_id,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return {"captured_at": "no photo yet", "stage_tag": "unknown"}
    return {"captured_at": _time_ago(row["captured_at"]), "stage_tag": row["stage_tag"] or "unknown"}

def get_gallery(batch_id):
    """Every photo for one batch, most recent first."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """SELECT captured_at, stage_tag FROM images
           WHERE batch_id = %s ORDER BY captured_at DESC""",
        (batch_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"captured_at": r["captured_at"].strftime("%Y-%m-%d"), "stage_tag": r["stage_tag"] or "unknown"}
        for r in rows
    ]


def fmt(value, unit=""):
    return f"{value}{unit}" if value is not None else "—"


def render_rack_card(rack):
    status = rack["status"]
    card_class = "room-card" if status == "ok" else f"room-card {status if status != 'offline' else 'bad'}"
    room = get_room_events(rack["room_id"])
    actuator_html = "".join(
        f'<span class="actuator-chip {"on" if a["state"] else ""}">'
        f'<span class="dot {"dot-ok" if a["state"] else "dot-offline"}"></span>{a["actuator_name"]}</span>'
        for a in room["actuators"]
    )
    snapshot = get_latest_snapshot(rack["rack_id"])

    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"""
        <div class="{card_class}">
            <div class="room-header">
                <div class="room-name">{rack['display_name']}</div>
                <span class="badge {badge_class(status)}">{status}</span>
            </div>
            <div class="room-metrics">
                <div class="room-metric"><div class="room-metric-label">Temp</div>
                    <div class="room-metric-value">{fmt(rack['temperature'], '°C')}</div></div>
                <div class="room-metric"><div class="room-metric-label">Humidity</div>
                    <div class="room-metric-value">{fmt(rack['humidity'], '%')}</div></div>
                <div class="room-metric"><div class="room-metric-label">CO₂</div>
                    <div class="room-metric-value">{fmt(rack['co2'], 'ppm')}</div></div>
                <div class="room-metric"><div class="room-metric-label">Light</div>
                    <div class="room-metric-value">{fmt(rack['light'], 'lux')}</div></div>
                <div class="room-metric"><div class="room-metric-label">Substrate moisture</div>
                    <div class="room-metric-value">{fmt(rack['substrate_moisture'], '%')}</div></div>
            </div>
            <div class="actuator-row">{actuator_html}</div>
            <div class="room-status" style="margin-top:10px;">
                Updated {rack['last_update']} · fans/humidifier shared with {rack['room_code']}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="snapshot-thumb">📷<br>{snapshot["captured_at"]}</div>', unsafe_allow_html=True)
        st.caption(f"Stage: {snapshot['stage_tag'].replace('_', ' ')}")


def render_gallery(batch_id):
    images = get_gallery(batch_id)
    tiles = "".join(
        f'<div class="gallery-item">📷<div>{img["captured_at"]}</div><div>{img["stage_tag"].replace("_"," ")}</div></div>'
        for img in images
    )
    st.markdown(f'<div class="gallery-grid">{tiles}</div>', unsafe_allow_html=True)


def main():
    inject_css()
    page_header("Smart Mushroom Farm", "Live monitoring",
                "Real-time readings per rack; door and actuator status per room.")

    racks = get_racks()
    online = sum(1 for r in racks if r["status"] != "offline")
    st.markdown(f"<div style='color:#8A8270; font-size:13px; margin-bottom:16px;'>"
                f"{online}/{len(racks)} racks reporting across 2 rooms</div>", unsafe_allow_html=True)

    for rack in racks:
        render_rack_card(rack)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if not racks:
        st.info("No racks registered yet. Once the Raspberry Pi starts sending "
                 "sensor data, racks will appear here automatically.")
        return

    # Drill-down
    card_open("Rack detail")
    rack_names = {r["display_name"]: r["rack_id"] for r in racks}
    selected_name = st.selectbox("Select a rack", list(rack_names.keys()), label_visibility="collapsed")
    selected_id = rack_names[selected_name]
    selected_rack = next(r for r in racks if r["rack_id"] == selected_id)
    detail = get_rack_detail(selected_id)
    room = get_room_events(selected_rack["room_id"])

    d1, d2, d3 = st.columns(3)
    d1.metric("Substrate temp", fmt(detail["substrate_temp"], "°C"))
    d2.metric("Air exchange rate", fmt(detail["ach"], " ACH"))
    d3.metric("Door events (24h)", fmt(room["door_events_24h"]))
    st.markdown(f"<div style='color:#8A8270; font-size:13px; margin-top:2px;'>"
                f"Door events are counted per room ({selected_rack['room_code']}) — "
                f"every rack in that room shares the same door.</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#8A8270; font-size:13px; margin-top:8px;'>"
                f"{detail['batch_code']} · currently in "
                f"<b style='color:#2B2318'>{detail['stage'].replace('_',' ').title()}</b></div>",
                unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='card-title' style='font-size:13px;'>Growth gallery — this batch</div>", unsafe_allow_html=True)
    render_gallery(selected_rack["batch_id"])
    card_close()


if __name__ == "__main__":
    main()