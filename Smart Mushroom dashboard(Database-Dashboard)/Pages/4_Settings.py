"""
Smart Mushroom Farm — Settings
Alert thresholds + sensor metadata, matching the real `sensors` table
your database team built (node_id, model, room/rack, calibration,
interval, connectivity).

Note: the schema currently has `connectivity` but not `power` — the
BRIDGE-AI doc asks for both. Flagged for the database team; not shown
here since it isn't real data yet.
"""

import streamlit as st
from theme import inject_css, page_header, card_open, card_close

st.set_page_config(page_title="Settings · Smart Mushroom Farm", page_icon="🍄", layout="wide")

# ─────────────────────────────────────────────────────────────
# MOCK DATA — replace with real reads/writes against the MySQL server
# ─────────────────────────────────────────────────────────────

def get_thresholds():
    """Mirrors: system_settings key/value pairs, one row per bound"""
    return {
        "Temperature (°C)": {"min": 20.0, "max": 24.0},
        "Humidity (%)": {"min": 85.0, "max": 95.0},
        "CO₂ (ppm)": {"min": 0.0, "max": 800.0},
        "Light (lux)": {"min": 200.0, "max": 500.0},
        "Substrate moisture (%)": {"min": 55.0, "max": 70.0},
    }

def get_sensors():
    """Mirrors: SELECT * FROM sensors"""
    return [
        {"node_id": "TMP-01", "sensor_type": "Temperature", "unit": "°C", "model": "DHT22",
         "room_id": "Room 1 · Rack A", "calibration_date": "2026-06-02", "interval_seconds": 30, "connectivity": "wifi"},
        {"node_id": "HUM-01", "sensor_type": "Humidity", "unit": "%", "model": "DHT22",
         "room_id": "Room 1 · Rack A", "calibration_date": "2026-06-02", "interval_seconds": 30, "connectivity": "wifi"},
        {"node_id": "CO2-01", "sensor_type": "CO₂ (NDIR)", "unit": "ppm", "model": "MH-Z19B",
         "room_id": "Room 1 · Rack A", "calibration_date": "2026-05-28", "interval_seconds": 60, "connectivity": "wifi"},
        {"node_id": "LUX-01", "sensor_type": "Light", "unit": "lux", "model": "BH1750",
         "room_id": "Room 1 · Rack A", "calibration_date": "2026-06-02", "interval_seconds": 60, "connectivity": "wifi"},
        {"node_id": "SUB-01", "sensor_type": "Substrate temp", "unit": "°C", "model": "DS18B20",
         "room_id": "Room 1 · Rack A, Bag 4", "calibration_date": "2026-05-28", "interval_seconds": 60, "connectivity": "wired"},
        {"node_id": "MOI-01", "sensor_type": "Substrate moisture", "unit": "%", "model": "Capacitive FDR",
         "room_id": "Room 1 · Rack A, Bag 4", "calibration_date": "2026-05-28", "interval_seconds": 60, "connectivity": "wired"},
    ]


def render_threshold_editor():
    thresholds = get_thresholds()
    card_open("Alert thresholds", "Values outside these ranges trigger a warning across the dashboard.")
    for variable, bounds in thresholds.items():
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.markdown(f"<div style='padding-top:8px; font-size:14px; color:#4A4433;'>{variable}</div>",
                    unsafe_allow_html=True)
        c2.number_input("Min", value=bounds["min"], key=f"min_{variable}", label_visibility="collapsed")
        c3.number_input("Max", value=bounds["max"], key=f"max_{variable}", label_visibility="collapsed")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Save thresholds"):
        st.success("Thresholds saved.")
    card_close()


def render_sensor_table():
    sensors = get_sensors()
    card_open("Sensor metadata", "Pulled from the sensors table — node ID, model, location, calibration, connectivity.")
    rows = "".join(
        f"<tr><td>{s['node_id']}</td><td>{s['sensor_type']}</td><td>{s['model']}</td>"
        f"<td>{s['room_id']}</td><td>{s['calibration_date']}</td><td>{s['interval_seconds']}s</td>"
        f"<td>{s['connectivity']}</td></tr>"
        for s in sensors
    )
    st.markdown(f"""
    <table class="meta-table">
        <tr><th>Node ID</th><th>Type</th><th>Model</th><th>Location</th><th>Last calibrated</th><th>Interval</th><th>Connectivity</th></tr>
        {rows}
    </table>
    """, unsafe_allow_html=True)
    card_close()
    st.markdown("<div style='color:#8A8270; font-size:12px;'>"
                "Note: the current schema doesn't store power source (mains/battery/solar) per sensor — "
                "worth raising with the database team if you want that column added.</div>", unsafe_allow_html=True)


def main():
    inject_css()
    page_header("Smart Mushroom Farm", "Settings",
                "Configure alert thresholds and manage sensor metadata.")
    render_threshold_editor()
    render_sensor_table()


if __name__ == "__main__":
    main()
