"""
check_data.py — quick diagnostic for why Home.py shows "—" instead of averages.

HOW TO RUN:
1. Copy this file into the SAME folder as db.py and Home.py.
2. Open a terminal in that folder.
3. Make sure your MySQL env vars are set the same way you set them to run
   the dashboard (MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD) — if you're not
   sure, just run it the same way you normally run "streamlit run Home.py",
   but instead type:
       python check_data.py
4. Read the printed output — it tells you in plain English what's wrong.
"""

from db import get_connection

EXPECTED_TYPES = {"temperature", "humidity", "co2", "light", "substrate_moisture"}

def main():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    print("=" * 60)
    print("CHECK 1: What sensor_type values actually exist in `sensors`?")
    print("=" * 60)
    cur.execute("SELECT DISTINCT sensor_type FROM sensors")
    found_types = {row["sensor_type"] for row in cur.fetchall()}
    print("Found:   ", found_types)
    print("Expected:", EXPECTED_TYPES)
    missing = EXPECTED_TYPES - found_types
    extra = found_types - EXPECTED_TYPES
    if missing:
        print(f"⚠️  PROBLEM: these expected types are MISSING: {missing}")
        print("   -> Either Charles needs to rename them, or data.py needs updating.")
    if extra:
        print(f"ℹ️  Note: these exist but aren't used by data.py: {extra}")
    if not missing:
        print("✅ Sensor type names look fine.")

    print()
    print("=" * 60)
    print("CHECK 2: How recent is the newest reading per sensor?")
    print("=" * 60)
    cur.execute("""
        SELECT s.sensor_id, s.sensor_type, s.rack_id, MAX(sr.recorded_at) AS latest
        FROM sensors s
        LEFT JOIN sensor_readings sr ON sr.sensor_id = s.sensor_id
        GROUP BY s.sensor_id, s.sensor_type, s.rack_id
        ORDER BY latest DESC
    """)
    rows = cur.fetchall()
    if not rows:
        print("⚠️  PROBLEM: no rows in `sensors` at all.")
    for r in rows:
        if r["latest"] is None:
            print(f"⚠️  sensor_id={r['sensor_id']} ({r['sensor_type']}, rack_id={r['rack_id']}): NO READINGS YET")
        else:
            print(f"   sensor_id={r['sensor_id']} ({r['sensor_type']}, rack_id={r['rack_id']}): latest = {r['latest']}")
    print()
    print("If every 'latest' timestamp above is more than 15 minutes old,")
    print("that's why Home shows dashes — the dashboard treats stale data as 'offline'.")

    print()
    print("=" * 60)
    print("CHECK 3: Do any sensors have a missing rack_id?")
    print("=" * 60)
    cur.execute("SELECT sensor_id, sensor_type FROM sensors WHERE rack_id IS NULL")
    orphans = cur.fetchall()
    if orphans:
        print(f"⚠️  PROBLEM: {len(orphans)} sensor(s) have no rack_id set:")
        for o in orphans:
            print(f"   sensor_id={o['sensor_id']} ({o['sensor_type']})")
    else:
        print("✅ Every sensor has a rack_id.")

    cur.close()
    conn.close()

    print()
    print("=" * 60)
    print("DONE. Send Claude everything printed above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
