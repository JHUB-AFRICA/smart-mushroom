
"""
Shared visual theme for the Smart Mushroom Farm dashboard.
Import inject_css() at the top of every page so Home, Live Monitoring,
Graphs, and Settings all look like one product instead of four.
"""

import base64
import os
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Work+Sans:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap');

:root {
    --soil: #2B2318;
    --soil-light: #4A3B28;
    --cream: #F4EEDF;
    --moss: #6B8A55;
    --moss-light: #9DBB80;
    --amber: #C98A3B;
    --rust: #B4552F;
    --line: #EAE3D3;
    --muted: #8A8270;
    --text: #4A4433;
}

#MainMenu, footer {visibility: hidden;}
header {background-color: transparent;}
/* keep the sidebar collapse/expand arrow visible and clickable — hiding
   the whole header (previous rule) hid this control along with it */
header [data-testid="stHeaderActionElements"] {visibility: visible;}
.block-container {padding-top: 1.5rem; max-width: 1200px;}
body, .stApp {background-color: #FAF7F0;}
* {font-family: 'Work Sans', sans-serif;}

/* Force native Streamlit widget text to stay dark even if the user's
   system/browser prefers dark mode and .streamlit/config.toml is ignored
   by the hosting platform — otherwise radio/selectbox labels can render
   in a light colour that's invisible against our light cards. */
.stApp, .stApp * {color: var(--text);}
div[data-testid="stRadio"] label, div[data-testid="stRadio"] p,
div[data-testid="stSelectbox"] label, div[data-testid="stWidgetLabel"] p,
.stMarkdown, .stMarkdown p {color: var(--text) !important;}
div[data-testid="stSidebar"] * {color: var(--cream) !important;}
.page-eyebrow {
    color: var(--moss);
    font-size: 13px; font-weight: 600;
    letter-spacing: 0.06em; text-transform: uppercase;
    margin-bottom: 4px;
}
.page-title {
    font-family: 'Fraunces', serif;
    font-weight: 500; font-size: 30px;
    color: var(--soil); margin-bottom: 4px;
}
.page-sub {color: var(--muted); font-size: 14px; margin-bottom: 24px;}

/* ---------- HERO (Home page only) ---------- */
.hero {
    position: relative; border-radius: 20px; overflow: hidden; min-height: 300px;
    margin-bottom: 24px;
    /* base gradient only — the photo is layered on top via an inline
       style (see theme.hero_style() in Python) because Streamlit
       doesn't serve local folders as web paths, so a CSS url() to a
       relative file silently fails. */
    background-image: linear-gradient(120deg, #2B2318 0%, #4A3B28 100%);
    background-size: cover; background-position: center;
    padding: 36px 40px; display: flex; flex-direction: column; justify-content: space-between;
}
.hero-eyebrow {color: var(--moss-light); font-size: 13px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 10px;}
.hero-greeting {font-family: 'Fraunces', serif; font-weight: 500; font-size: 40px; color: var(--cream); line-height: 1.15; margin-bottom: 6px;}
.hero-sub {color: rgba(244,238,223,0.75); font-size: 15px;}

/* ---------- STAT CHIPS (light + dark variants) ---------- */
.chip-row {display: flex; gap: 14px; margin-top: 24px; flex-wrap: wrap;}
.chip {
    background: rgba(244,238,223,0.14); backdrop-filter: blur(14px);
    border: 1px solid rgba(244,238,223,0.22); border-radius: 14px;
    padding: 14px 18px; min-width: 140px;
}
.chip-label {color: rgba(244,238,223,0.65); font-size: 12px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 4px;}
.chip-value {font-family: 'JetBrains Mono', monospace; font-weight: 500; font-size: 22px; color: var(--cream);}
.chip-value .unit {font-size: 13px; opacity: 0.6; margin-left: 2px;}
.chip-range {color: rgba(244,238,223,0.5); font-size: 11px; margin-top: 2px;}

.chip-light {background: white; border: 1px solid var(--line);}
.chip-light .chip-label {color: var(--muted);}
.chip-light .chip-value {color: var(--soil);}
.chip-light .chip-range {color: #B5AC96;}

.dot {display:inline-block; width:7px; height:7px; border-radius:50%; margin-right:6px;}
.dot-ok {background: var(--moss-light);}
.dot-warn {background: var(--amber);}
.dot-bad {background: var(--rust);}
.dot-offline {background: #C7BFA9;}

/* ---------- SYSTEM HEALTH STRIP ---------- */
.health-strip {display: flex; gap: 24px; flex-wrap: wrap; align-items: center; margin-bottom: 24px; padding: 14px 20px; background: white; border: 1px solid var(--line); border-radius: 14px;}
.health-item {display: flex; align-items: center; font-size: 13px; color: var(--text); gap: 6px;}
.health-item b {font-weight: 600; color: var(--soil);}

/* ---------- GROW CYCLE STEPPER ---------- */
.stepper-card {background: white; border-radius: 16px; border: 1px solid var(--line); padding: 24px 28px; margin-bottom: 24px;}
.stepper-title {font-size: 14px; font-weight: 600; color: var(--soil); margin-bottom: 2px;}
.stepper-sub {font-size: 13px; color: var(--muted); margin-bottom: 20px;}
.stepper-track {display: flex; align-items: center;}
.step {display: flex; flex-direction: column; align-items: center; flex: 1; position: relative;}
.step-circle {width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 500; z-index: 2; border: 2px solid var(--line); background: white; color: #B5AC96;}
.step-circle.done {background: var(--moss); border-color: var(--moss); color: white;}
.step-circle.active {background: var(--amber); border-color: var(--amber); color: white;}
.step-label {font-size: 12px; margin-top: 8px; color: var(--muted); text-align: center;}
.step-label.active {color: var(--soil); font-weight: 600;}
.step-line {position: absolute; top: 15px; left: -50%; width: 100%; height: 2px; background: var(--line); z-index: 1;}
.step-line.done {background: var(--moss);}
.step:first-child .step-line {display: none;}

/* ---------- GENERIC CARD ---------- */
.card {background: white; border-radius: 16px; border: 1px solid var(--line); padding: 20px 22px; height: 100%; margin-bottom: 20px;}
.card-title {font-size: 14px; font-weight: 600; color: var(--soil); margin-bottom: 4px;}
.card-sub {font-size: 12px; color: var(--muted); margin-bottom: 14px;}

/* ---------- METRIC (small number card, e.g. power) ---------- */
.metric-card {background: white; border-radius: 16px; border: 1px solid var(--line); padding: 18px 20px;}
.metric-label {font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 6px;}
.metric-value {font-family: 'JetBrains Mono', monospace; font-size: 26px; font-weight: 500; color: var(--soil);}
.metric-value .unit {font-size: 14px; opacity: 0.5; margin-left: 3px;}
.metric-delta {font-size: 12px; margin-top: 4px;}
.metric-delta.up {color: var(--rust);}
.metric-delta.down {color: var(--moss);}

/* ---------- ALERTS ---------- */
.alert-row {display: flex; align-items: flex-start; gap: 10px; padding: 10px 0; border-bottom: 1px solid #F1ECDF; font-size: 13px; color: var(--text);}
.alert-row:last-child {border-bottom: none;}
.alert-time {color: var(--muted); font-size: 11px; margin-left: auto; white-space: nowrap;}

/* ---------- ROOM / RACK CARDS (Live Monitoring) ---------- */
.room-card {background: white; border-radius: 16px; border: 1px solid var(--line); padding: 18px 20px; margin-bottom: 16px;}
.room-card.warn {border-color: var(--amber);}
.room-card.bad {border-color: var(--rust);}
.room-header {display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;}
.room-name {font-weight: 600; color: var(--soil); font-size: 15px;}
.room-status {font-size: 12px; color: var(--muted);}
.room-metrics {display: flex; gap: 20px; flex-wrap: wrap;}
.room-metric {font-size: 13px;}
.room-metric-label {color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.03em;}
.room-metric-value {font-family: 'JetBrains Mono', monospace; font-weight: 500; color: var(--soil); font-size: 15px;}

/* ---------- BADGES ---------- */
.badge {display: inline-block; padding: 3px 10px; border-radius: 100px; font-size: 11px; font-weight: 600;}
.badge-ok {background: #EAF1E3; color: var(--moss);}
.badge-warn {background: #FBF0DF; color: var(--amber);}
.badge-bad {background: #F9E7E0; color: var(--rust);}
.badge-offline {background: #F1EEE6; color: #A69E88;}

/* ---------- SETTINGS TABLE ---------- */
.meta-table {width: 100%; border-collapse: collapse; font-size: 13px;}
.meta-table th {text-align: left; color: var(--muted); font-weight: 500; font-size: 11px; text-transform: uppercase; letter-spacing: 0.03em; padding: 8px 10px; border-bottom: 1px solid var(--line);}
.meta-table td {padding: 10px 10px; border-bottom: 1px solid #F1ECDF; color: var(--text);}

/* ---------- ACTUATOR CHIPS ---------- */
.actuator-row {display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px;}
.actuator-chip {display: flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 100px; font-size: 12px; font-weight: 500; border: 1px solid var(--line); background: #FAF7F0; color: var(--muted);}
.actuator-chip.on {background: #EAF1E3; border-color: var(--moss); color: var(--moss);}
.actuator-chip .dot {margin-right: 0;}

/* ---------- SEVERITY BADGES ---------- */
.badge-low {background: #EAF1E3; color: var(--moss);}
.badge-medium {background: #FBF0DF; color: var(--amber);}
.badge-high {background: #F9E7E0; color: var(--rust);}
.badge-critical {background: var(--rust); color: white;}

/* ---------- CAMERA / GALLERY ---------- */
.snapshot-thumb {width: 100%; aspect-ratio: 4/3; border-radius: 12px; background: linear-gradient(135deg, #E3DCC9, #F4EEDF); border: 1px solid var(--line); display: flex; align-items: center; justify-content: center; color: #B5AC96; font-size: 12px; cursor: pointer; overflow: hidden;}
.gallery-grid {display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px; margin-top: 12px;}
.gallery-item {aspect-ratio: 4/3; border-radius: 10px; background: linear-gradient(135deg, #E3DCC9, #F4EEDF); border: 1px solid var(--line); display: flex; flex-direction: column; align-items: center; justify-content: center; color: #A69E88; font-size: 11px; gap: 4px;}

/* ---------- TABS ---------- */
button[data-baseweb="tab"] {font-family: 'Work Sans', sans-serif !important; font-size: 14px !important; color: var(--muted) !important;}
button[data-baseweb="tab"][aria-selected="true"] {color: var(--soil) !important; font-weight: 600 !important;}
div[data-baseweb="tab-highlight"] {background-color: var(--moss) !important;}
div[data-baseweb="tab-border"] {background-color: var(--line) !important;}

/* Streamlit widget tweaks to match the palette */
div[data-testid="stSidebar"] {background-color: var(--soil);}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def status_class(status: str) -> str:
    return {"ok": "dot-ok", "warn": "dot-warn", "bad": "dot-bad", "offline": "dot-offline"}.get(status, "dot-ok")


def badge_class(status: str) -> str:
    return {"ok": "badge-ok", "warn": "badge-warn", "bad": "badge-bad", "offline": "badge-offline"}.get(status, "badge-ok")


def page_header(eyebrow: str, title: str, subtitle: str = ""):
    st.markdown(f"""
        <div class="page-eyebrow">{eyebrow}</div>
        <div class="page-title">{title}</div>
        <div class="page-sub">{subtitle}</div>
    """, unsafe_allow_html=True)


def stat_chip_html(label, value, unit, status, range_text, light=False):
    chip_cls = "chip chip-light" if light else "chip"
    return f"""
    <div class="{chip_cls}">
        <div class="chip-label"><span class="dot {status_class(status)}"></span>{label}</div>
        <div class="chip-value">{value}<span class="unit">{unit}</span></div>
        <div class="chip-range">Target {range_text}</div>
    </div>"""


def card_open(title: str, subtitle: str = ""):
    sub = f'<div class="card-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(f'<div class="card"><div class="card-title">{title}</div>{sub}', unsafe_allow_html=True)


def hero_style (image_filename="mushroom_hero.jpg"):
    """Returns an inline style attribute for the .hero div that layers the
    real photo under the gradient, if the file exists. Streamlit doesn't
    serve local folders as web paths, so instead of linking to the file
    (which silently fails), we read it and embed it as base64 — this
    always works, in any deployment, with zero extra config."""
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "assets", image_filename)
    if not os.path.exists(path):
        return ""  # falls back to the plain gradient already in the CSS
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    gradient = ("linear-gradient(100deg, rgba(43,35,24,0.94) 0%, rgba(43,35,24,0.75) 35%, "
                "rgba(43,35,24,0.25) 65%, rgba(43,35,24,0.05) 100%)")
    return f'style="background-image: {gradient}, url(data:image/{mime};base64,{b64});"'


def card_close():
    st.markdown('</div>', unsafe_allow_html=True)


def actuator_chip_html(name, is_on, note=""):
    cls = "actuator-chip on" if is_on else "actuator-chip"
    dot = "dot-ok" if is_on else "dot-offline"
    label = f"{name} · {note}" if note else name
    return f'<span class="{cls}"><span class="dot {dot}"></span>{label}</span>'


def severity_badge_class(severity: str) -> str:
    return {"low": "badge-low", "medium": "badge-medium",
            "high": "badge-high", "critical": "badge-critical"}.get(severity, "badge-low")