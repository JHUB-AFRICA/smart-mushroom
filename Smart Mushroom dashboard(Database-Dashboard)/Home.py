"""
Smart Mushroom Farm — Home / Overview page
JHUB Africa · JKUAT Smart Farm Zone
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from theme import inject_css, stat_chip_html, card_open, card_close, status_class, hero_style
from data import get_racks, average_conditions, get_system_health

st.set_page_config(page_title="Smart Mushroom Farm", page_icon="🍄", layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────────────────────
# MOCK DATA — replace bodies with calls into Charles's SQLite module
# ─────────────────────────────────────────────────────────────

def get_farmer_name():
    return "Caroline"

CHIP_UNITS = {"temperature": "°C", "humidity": "%", "co2": "ppm", "light": "lux"}
CHIP_LABELS = {"temperature": "Avg. Temperature", "humidity": "Avg. Humidity",
               "co2": "Avg. CO₂", "light": "Avg. Light"}
CHIP_RANGES = {"temperature": "20–24°C", "humidity": "85–95%",
               "co2": "<800ppm", "light": "200–500lux"}

def get_current_conditions():
    """Farm-wide average across every reporting rack — NOT a single sensor's
    latest reading. Averaged live from data.get_racks(); once real data is
    flowing this stays an average, just computed from real rows instead of
    mock ones. Returns (conditions_dict, racks_reporting, racks_total)."""
    racks = get_racks()
    averages, reporting, total = average_conditions(racks)
    conditions = {}
    for var in ["temperature", "humidity", "co2", "light"]:
        a = averages[var]
        conditions[var] = {
            "value": a["value"] if a["value"] is not None else "—",
            "unit": CHIP_UNITS[var], "status": a["status"], "range": CHIP_RANGES[var],
        }
    return conditions, reporting, total

def get_power_usage():
    return {"watts": 486, "delta_pct": -6.2, "breakdown": {"Fans": 180, "Humidifier": 210, "Lights": 60, "Controller": 36}}

def get_grow_cycle():
    stages = ["Inoculation", "Incubation", "Colonisation", "Pinning", "Fruiting", "Harvest"]
    return {"stages": stages, "current_index": 3, "day_in_stage": 4, "batch_id": "Batch 07"}

def get_trend_data():
    hours = [f"{h:02d}:00" for h in range(0, 24, 2)]
    temp = [21.8, 21.9, 22.0, 22.6, 23.1, 22.9, 22.5, 22.2, 22.0, 21.9, 21.8, 22.4]
    humidity = [88, 87, 86, 85, 84, 85, 87, 89, 90, 89, 88, 87]
    return hours, temp, humidity

def get_alerts():
    return [
        {"level": "warn", "text": "CO₂ trending up in Rack 3 — check ventilation schedule", "time": "12m ago"},
        {"level": "ok", "text": "Flush 2 humidity stable for 6 hours", "time": "1h ago"},
    ]


# ─────────────────────────────────────────────────────────────
# RENDER
# ─────────────────────────────────────────────────────────────

def render_hero():
    name = get_farmer_name()
    conditions, reporting, total = get_current_conditions()
    today = datetime.now().strftime("%A, %d %B %Y")
    chips_html = "".join(
        stat_chip_html(CHIP_LABELS[var], c["value"], c["unit"], c["status"], c["range"])
        for var, c in conditions.items()
    )
    st.markdown(f"""
    <div class="hero" {hero_style()}>
        <div>
            <div class="hero-eyebrow">JHUB Africa · Smart Mushroom Farm</div>
            <div class="hero-greeting">Welcome back, {name}</div>
            <div class="hero-sub">{today} · Averaged across {reporting}/{total} racks reporting</div>
        </div>
        <div class="chip-row">{chips_html}</div>
    </div>
    """, unsafe_allow_html=True)


def render_system_health():
    h = get_system_health()
    sensors_status = "ok" if h["sensors_online"] == h["sensors_total"] else "warn"
    st.markdown(f"""
    <div class="health-strip">
        <div class="health-item"><span class="dot {status_class(sensors_status)}"></span>
            Sensors <b>{h['sensors_online']}/{h['sensors_total']}</b> online</div>
        <div class="health-item"><span class="dot {status_class(h['esp32'])}"></span>ESP32 <b>connected</b></div>
        <div class="health-item"><span class="dot {status_class(h['raspberry_pi'])}"></span>Raspberry Pi <b>connected</b></div>
        <div class="health-item">Last sync <b>{h['last_sync']}</b></div>
    </div>
    """, unsafe_allow_html=True)


def render_grow_cycle():
    cycle = get_grow_cycle()
    stages, current = cycle["stages"], cycle["current_index"]
    steps_html = ""
    for i, stage in enumerate(stages):
        if i < current:
            circle_class, line_class, label_class, icon = "done", "done", "", "✓"
        elif i == current:
            circle_class, line_class, label_class, icon = "active", "done", "active", str(i + 1)
        else:
            circle_class, line_class, label_class, icon = "", "", "", str(i + 1)
        steps_html += f"""<div class="step"><div class="step-line {line_class}"></div>
            <div class="step-circle {circle_class}">{icon}</div>
            <div class="step-label {label_class}">{stage}</div></div>"""
    st.markdown(f"""
    <div class="stepper-card">
        <div class="stepper-title">Grow cycle — {cycle['batch_id']}</div>
        <div class="stepper-sub">Day {cycle['day_in_stage']} of current stage</div>
        <div class="stepper-track">{steps_html}</div>
    </div>
    """, unsafe_allow_html=True)


def render_power_card():
    p = get_power_usage()
    delta_class = "down" if p["delta_pct"] < 0 else "up"
    arrow = "↓" if p["delta_pct"] < 0 else "↑"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Power draw</div>
        <div class="metric-value">{p['watts']}<span class="unit">W</span></div>
        <div class="metric-delta {delta_class}">{arrow} {abs(p['delta_pct'])}% vs yesterday</div>
    </div>
    """, unsafe_allow_html=True)


def render_trend_chart():
    hours, temp, humidity = get_trend_data()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hours, y=temp, name="Temp (°C)", line=dict(color="#B4552F", width=2.5)))
    fig.add_trace(go.Scatter(x=hours, y=humidity, name="Humidity (%)", line=dict(color="#6B8A55", width=2.5), yaxis="y2"))
    fig.update_layout(
        height=240, margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Work Sans", size=12, color="#4A4433"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(color="#4A4433")),
        xaxis=dict(showgrid=False, tickfont=dict(color="#4A4433")),
        yaxis=dict(title=dict(text="°C", font=dict(color="#4A4433")), showgrid=True,
                    gridcolor="#F1ECDF", tickfont=dict(color="#4A4433")),
        yaxis2=dict(title=dict(text="%", font=dict(color="#4A4433")), overlaying="y",
                    side="right", showgrid=False, tickfont=dict(color="#4A4433")),
        hoverlabel=dict(bgcolor="white", font=dict(color="#2B2318", size=12), bordercolor="#EAE3D3"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, theme=None)


def render_alerts():
    alerts = get_alerts()
    rows = "".join(
        f'<div class="alert-row"><span class="dot {status_class(a["level"])}" style="margin-top:5px;"></span>'
        f'{a["text"]}<span class="alert-time">{a["time"]}</span></div>'
        for a in alerts
    )
    card_open("Active alerts")
    st.markdown(rows, unsafe_allow_html=True)
    card_close()


def main():
    inject_css()
    render_hero()
    render_system_health()
    render_grow_cycle()

    col1, col2 = st.columns([2, 1])
    with col1:
        card_open("24h environment trend")
        render_trend_chart()
        card_close()
    with col2:
        render_power_card()
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        render_alerts()


if __name__ == "__main__":
    main()