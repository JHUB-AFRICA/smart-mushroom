"""
Smart Mushroom Farm — Graphs
Historical trends with filters, and a CSV export satisfying the
BRIDGE-AI "manual Excel/CSV export" requirement.
"""

import math
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from theme import inject_css, page_header, card_open, card_close

st.set_page_config(page_title="Graphs · Smart Mushroom Farm", page_icon="🍄", layout="wide", initial_sidebar_state="expanded")

VARIABLES = {
    "Temperature (°C)": {"color": "#B4552F", "target": (20, 24)},
    "Humidity (%)": {"color": "#6B8A55", "target": (85, 95)},
    "CO₂ (ppm)": {"color": "#C98A3B", "target": (0, 800)},
    "Light (lux)": {"color": "#8A8270", "target": (200, 500)},
    "Substrate moisture (%)": {"color": "#4A3B28", "target": (55, 70)},
}
ROOMS = ["Room 1 · Rack A", "Room 1 · Rack B", "Room 2 · Rack A", "Room 2 · Rack B"]

# Range options: label -> hours. Short ranges sample every few minutes so
# you can actually see movement; long ranges sample hourly so point counts
# stay reasonable.
RANGE_OPTIONS = {
    "1h": 1, "3h": 3, "6h": 6, "12h": 12,
    "1d": 24, "3d": 72, "7d": 168, "14d": 336, "30d": 720,
}


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Plotly's fillcolor validator rejects 8-digit hex (#RRGGBBAA) on some
    versions — convert to rgba(...) instead, which is always accepted."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ─────────────────────────────────────────────────────────────
# MOCK DATA — replace with:
#   SELECT recorded_at, sensor_value FROM sensor_readings
#   JOIN sensors ON sensors.sensor_id = sensor_readings.sensor_id
#   WHERE sensor_type = ? AND room_id = ? AND recorded_at BETWEEN ? AND ?
# ─────────────────────────────────────────────────────────────

def get_series(variable, room, hours=168):
    """Generates a believable mock reading: a real day/night cycle (period
    = 24h, so short windows actually show movement, not a flat segment)
    plus small sensor-noise wobble so even a 1h view isn't a dead-straight
    line."""
    base = {"Temperature (°C)": 22, "Humidity (%)": 87, "CO₂ (ppm)": 700,
            "Light (lux)": 340, "Substrate moisture (%)": 62}[variable]
    daily_amp = {"Temperature (°C)": 1.4, "Humidity (%)": 3.5, "CO₂ (ppm)": 180,
                 "Light (lux)": 60, "Substrate moisture (%)": 1.5}[variable]
    noise_amp = {"Temperature (°C)": 0.2, "Humidity (%)": 0.6, "CO₂ (ppm)": 25,
                 "Light (lux)": 8, "Substrate moisture (%)": 0.3}[variable]
    room_offset = ROOMS.index(room) * 0.6

    # Sample resolution scales with range: minutes for short windows,
    # hourly for long ones, capped so we never generate an absurd number
    # of points.
    interval_minutes = 5 if hours <= 6 else 15 if hours <= 24 else 60
    n_points = min(int(hours * 60 / interval_minutes), 720)

    now = datetime.now()
    start = now - timedelta(hours=hours)
    xs, ys = [], []
    for i in range(n_points + 1):
        t = start + timedelta(minutes=i * interval_minutes)
        hour_of_day = t.hour + t.minute / 60
        daily_cycle = math.sin((hour_of_day - 6) / 24 * 2 * math.pi)  # low pre-dawn, peak mid-afternoon
        wobble = noise_amp * math.sin(i / 2.3) * math.cos(i / 5.1)
        value = base + room_offset + daily_amp * daily_cycle + wobble
        xs.append(t)
        ys.append(round(value, 1))
    return xs, ys


def render_chart(variable, room, hours):
    xs, ys = get_series(variable, room, hours)
    cfg = VARIABLES[variable]
    lo, hi = cfg["target"]

    # Explicit y-axis range so real variation is visible instead of being
    # crushed by the "fill to zero" area forcing the axis to include 0.
    y_min, y_max = min(ys + [lo]), max(ys + [hi])
    pad = max((y_max - y_min) * 0.15, 0.5)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xs, y=ys, name=variable, line=dict(color=cfg["color"], width=2.5),
        fill="tozeroy", fillcolor=hex_to_rgba(cfg["color"], 0.1),
        hovertemplate="%{x|%b %d, %H:%M}<br><b>%{y}</b><extra></extra>",
    ))
    fig.add_hrect(
        y0=lo, y1=hi, fillcolor="#6B8A55", opacity=0.08, line_width=0,
        annotation_text=f"Target {lo}–{hi}", annotation_position="top left",
        annotation_font=dict(color="#4A4433", size=11, family="Work Sans"),
    )
    fig.update_layout(
        height=340, margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Work Sans", size=12, color="#4A4433"),
        xaxis=dict(showgrid=False, tickfont=dict(color="#4A4433")),
        yaxis=dict(showgrid=True, gridcolor="#F1ECDF", tickfont=dict(color="#4A4433"),
                    range=[y_min - pad, y_max + pad]),
        showlegend=False,
        hoverlabel=dict(bgcolor="white", font=dict(color="#2B2318", size=12), bordercolor="#EAE3D3"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, theme=None)
    return xs, ys


def render_room_comparison(variable, hours):
    fig = go.Figure()
    palette = ["#B4552F", "#6B8A55", "#C98A3B", "#8A8270"]
    all_data = {}
    xs = []
    all_ys = []
    for i, room in enumerate(ROOMS):
        xs, ys = get_series(variable, room, hours)
        all_data[room] = ys
        all_ys.extend(ys)
        fig.add_trace(go.Scatter(
            x=xs, y=ys, name=room, line=dict(color=palette[i], width=2),
            hovertemplate="%{x|%b %d, %H:%M}<br><b>%{y}</b><extra>" + room + "</extra>",
        ))
    y_min, y_max = min(all_ys), max(all_ys)
    pad = max((y_max - y_min) * 0.15, 0.5)
    fig.update_layout(
        height=340, margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Work Sans", size=12, color="#4A4433"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(color="#4A4433")),
        xaxis=dict(showgrid=False, tickfont=dict(color="#4A4433")),
        yaxis=dict(title=dict(text=variable, font=dict(color="#4A4433")), showgrid=True,
                    gridcolor="#F1ECDF", tickfont=dict(color="#4A4433"), range=[y_min - pad, y_max + pad]),
        hoverlabel=dict(bgcolor="white", font=dict(color="#2B2318", size=12), bordercolor="#EAE3D3"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, theme=None)
    return xs, all_data


def main():
    inject_css()
    page_header("Smart Mushroom Farm", "Graphs",
                "Explore trends by variable, compare rooms, or export the raw readings.")

    mode = st.radio("View", ["Single room over time", "Compare rooms"], horizontal=True, label_visibility="collapsed")

    f1, f2, f3 = st.columns([1.2, 1.2, 1])
    with f1:
        variable = st.selectbox("Variable", list(VARIABLES.keys()))
    with f2:
        room = st.selectbox("Room", ROOMS) if mode == "Single room over time" else None
    with f3:
        range_label = st.selectbox("Range", list(RANGE_OPTIONS.keys()), index=6)  # default 7d
        hours = RANGE_OPTIONS[range_label]

    card_open(variable, room if mode == "Single room over time" else "All rooms compared")
    if mode == "Single room over time":
        xs, ys = render_chart(variable, room, hours)
        export_df = pd.DataFrame({"recorded_at": xs, "sensor_value": ys, "room": room, "variable": variable})
    else:
        xs, all_data = render_room_comparison(variable, hours)
        export_df = pd.DataFrame({"recorded_at": xs, **all_data})
    card_close()

    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown("<div style='color:#8A8270; font-size:12px; padding-top:8px;'>"
                    "Shaded band and label mark the target range from your BRIDGE-AI spec.</div>", unsafe_allow_html=True)
    with c2:
        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download CSV", data=csv,
                            file_name=f"{variable.split(' ')[0].lower()}_{range_label}.csv",
                            mime="text/csv", use_container_width=True)


if __name__ == "__main__":
    main()