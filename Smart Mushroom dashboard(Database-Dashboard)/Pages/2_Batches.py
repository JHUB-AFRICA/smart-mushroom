"""
Smart Mushroom Farm — Batches
Batch setup + phenology, yield & biological efficiency, and
contamination/event records — organized as tabs on one page.

Mock data mirrors: batches, phenology_events, yield_records,
contamination_records, abiotic_stress_events, door_events,
power_water_interruptions.
"""

import streamlit as st
from theme import inject_css, page_header, card_open, card_close, severity_badge_class

st.set_page_config(page_title="Batches · Smart Mushroom Farm", page_icon="🍄", layout="wide")

STAGES = ["inoculation", "incubation", "full_colonisation", "transfer_to_fruiting",
          "first_pins", "flush", "harvest", "end_of_cycle"]

# ─────────────────────────────────────────────────────────────
# MOCK DATA — replace bodies with real MySQL queries
# ─────────────────────────────────────────────────────────────

def get_batches():
    """Mirrors: SELECT * FROM batches"""
    return [
        {"batch_id": 7, "batch_code": "B2026-07", "room_code": "Room 1", "strain_code": "Oyster PoHu",
         "spawn_type": "grain", "spawn_rate_pct": 5.0, "substrate_composition": "70% wheat straw, 30% sawdust",
         "substrate_dry_weight_kg": 12.0, "substrate_moisture_pct": 62.0,
         "inoculation_date": "2026-07-14", "status": "active"},
        {"batch_id": 6, "batch_code": "B2026-06", "room_code": "Room 2", "strain_code": "Oyster PoHu",
         "spawn_type": "sawdust", "spawn_rate_pct": 4.5, "substrate_composition": "80% wheat straw, 20% sawdust",
         "substrate_dry_weight_kg": 11.5, "substrate_moisture_pct": 60.0,
         "inoculation_date": "2026-06-20", "status": "active"},
        {"batch_id": 5, "batch_code": "B2026-05", "room_code": "Room 2", "strain_code": "Shiitake LE-3",
         "spawn_type": "grain", "spawn_rate_pct": 5.5, "substrate_composition": "90% sawdust, 10% bran",
         "substrate_dry_weight_kg": 13.0, "substrate_moisture_pct": 58.0,
         "inoculation_date": "2026-05-30", "status": "completed"},
    ]

def get_phenology(batch_id):
    """Mirrors: SELECT stage, event_date FROM phenology_events WHERE batch_id = ? ORDER BY event_date"""
    data = {
        7: [{"stage": "inoculation", "event_date": "2026-07-14"}, {"stage": "incubation", "event_date": "2026-07-16"},
            {"stage": "full_colonisation", "event_date": "2026-07-30"}, {"stage": "transfer_to_fruiting", "event_date": "2026-08-02"},
            {"stage": "first_pins", "event_date": "2026-08-06"}],
        6: [{"stage": "inoculation", "event_date": "2026-06-20"}, {"stage": "incubation", "event_date": "2026-06-22"},
            {"stage": "full_colonisation", "event_date": "2026-07-05"}, {"stage": "transfer_to_fruiting", "event_date": "2026-07-09"},
            {"stage": "first_pins", "event_date": "2026-07-13"}, {"stage": "flush", "event_date": "2026-07-20"}],
        5: [{"stage": "inoculation", "event_date": "2026-05-30"}, {"stage": "incubation", "event_date": "2026-06-01"},
            {"stage": "full_colonisation", "event_date": "2026-06-14"}, {"stage": "transfer_to_fruiting", "event_date": "2026-06-18"},
            {"stage": "first_pins", "event_date": "2026-06-22"}, {"stage": "flush", "event_date": "2026-06-29"},
            {"stage": "harvest", "event_date": "2026-07-06"}, {"stage": "end_of_cycle", "event_date": "2026-07-08"}],
    }
    return data[batch_id]

def get_yield_records(batch_id):
    """Mirrors: SELECT flush_number, harvest_date, fresh_weight_kg FROM yield_records WHERE batch_id = ?"""
    data = {
        7: [],
        6: [{"flush_number": 1, "harvest_date": "2026-07-20", "fresh_weight_kg": 3.8}],
        5: [{"flush_number": 1, "harvest_date": "2026-07-06", "fresh_weight_kg": 5.1},
            {"flush_number": 2, "harvest_date": "2026-07-14", "fresh_weight_kg": 3.2},
            {"flush_number": 3, "harvest_date": "2026-07-21", "fresh_weight_kg": 1.6}],
    }
    return data[batch_id]

def get_contamination(batch_id):
    """Mirrors: SELECT * FROM contamination_records WHERE batch_id = ?"""
    data = {
        7: [], 6: [{"contamination_type": "Green mold (Trichoderma)", "severity": "medium",
                    "date_observed": "2026-07-25", "action_taken": "Isolated affected bags, increased airflow"}],
        5: [],
    }
    return data[batch_id]

def get_abiotic_events(batch_id):
    """Mirrors: SELECT * FROM abiotic_stress_events WHERE batch_id = ?"""
    data = {
        7: [{"stress_type": "power_outage", "start_time": "2026-08-05 14:20", "end_time": "2026-08-05 16:05", "severity": "low"}],
        6: [], 5: [],
    }
    return data[batch_id]


def render_stage_progress(phenology):
    completed_stages = [e["stage"] for e in phenology]
    current = completed_stages[-1] if completed_stages else STAGES[0]
    current_idx = STAGES.index(current)
    rows = ""
    for i, stage in enumerate(STAGES):
        if i < current_idx:
            cls, icon = "done", "✓"
        elif i == current_idx:
            cls, icon = "active", str(i + 1)
        else:
            cls, icon = "", str(i + 1)
        date = next((e["event_date"] for e in phenology if e["stage"] == stage), "")
        rows += f"""<div class="step"><div class="step-line {'done' if i <= current_idx else ''}"></div>
            <div class="step-circle {cls}">{icon}</div>
            <div class="step-label {'active' if i == current_idx else ''}">{stage.replace('_',' ').title()}<br>
            <span style='font-size:10px; opacity:0.6'>{date}</span></div></div>"""
    st.markdown(f'<div class="stepper-track">{rows}</div>', unsafe_allow_html=True)


def render_overview_tab(batch):
    card_open("Batch setup")
    c1, c2, c3 = st.columns(3)
    c1.metric("Substrate dry weight", f"{batch['substrate_dry_weight_kg']} kg")
    c2.metric("Moisture at filling", f"{batch['substrate_moisture_pct']}%")
    c3.metric("Spawn rate", f"{batch['spawn_rate_pct']}%")
    st.markdown(f"""
        <div style='font-size:13px; color:#4A4433; margin-top:8px; line-height:1.8;'>
        <b>Strain:</b> {batch['strain_code']} &nbsp;·&nbsp; <b>Spawn type:</b> {batch['spawn_type']}<br>
        <b>Substrate composition:</b> {batch['substrate_composition']}<br>
        <b>Inoculated:</b> {batch['inoculation_date']} &nbsp;·&nbsp; <b>Room:</b> {batch['room_code']}
        </div>
    """, unsafe_allow_html=True)
    card_close()

    card_open("Growth stage progress")
    render_stage_progress(get_phenology(batch["batch_id"]))
    card_close()


def render_yield_tab(batch):
    records = get_yield_records(batch["batch_id"])
    total_yield = sum(r["fresh_weight_kg"] for r in records)
    be_pct = (total_yield / batch["substrate_dry_weight_kg"] * 100) if batch["substrate_dry_weight_kg"] else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total yield", f"{total_yield:.1f} kg")
    c2.metric("Flushes harvested", len(records))
    c3.metric("Biological efficiency", f"{be_pct:.1f}%")

    card_open("Yield per flush")
    if records:
        rows = "".join(
            f"<tr><td>Flush {r['flush_number']}</td><td>{r['harvest_date']}</td><td>{r['fresh_weight_kg']} kg</td></tr>"
            for r in records
        )
        st.markdown(f"""<table class="meta-table">
            <tr><th>Flush</th><th>Harvest date</th><th>Fresh weight</th></tr>{rows}</table>""",
            unsafe_allow_html=True)
    else:
        st.markdown("<div style='color:#8A8270; font-size:13px;'>No flushes harvested yet for this batch.</div>",
                    unsafe_allow_html=True)
    card_close()
    st.markdown("<div style='color:#8A8270; font-size:12px;'>"
                "BE% = total fresh yield ÷ substrate dry weight × 100</div>", unsafe_allow_html=True)


def render_records_tab(batch):
    contamination = get_contamination(batch["batch_id"])
    abiotic = get_abiotic_events(batch["batch_id"])

    card_open("Contamination / anomaly records")
    if contamination:
        for c in contamination:
            st.markdown(f"""
            <div class="alert-row">
                <span class="badge {severity_badge_class(c['severity'])}">{c['severity']}</span>
                &nbsp;<b>{c['contamination_type']}</b> — {c['date_observed']}
                <div style='width:100%; margin-top:4px; color:#8A8270;'>{c['action_taken']}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<div style='color:#8A8270; font-size:13px;'>No contamination recorded for this batch.</div>",
                    unsafe_allow_html=True)
    with st.form(f"add_contamination_{batch['batch_id']}"):
        st.markdown("<div style='font-size:13px; font-weight:600; margin-top:8px;'>Log new contamination</div>",
                    unsafe_allow_html=True)
        ct = st.text_input("Type", placeholder="e.g. Green mold")
        sev = st.selectbox("Severity", ["low", "medium", "high", "critical"])
        action = st.text_area("Action taken", height=70)
        if st.form_submit_button("Log record"):
            st.success("Recorded (mock — wire to database to persist).")
    card_close()

    card_open("Abiotic stress events", "Overheating, RH excursions, waterlogging, power/water interruptions.")
    if abiotic:
        for e in abiotic:
            st.markdown(f"""
            <div class="alert-row">
                <span class="badge {severity_badge_class(e['severity'])}">{e['severity']}</span>
                &nbsp;<b>{e['stress_type'].replace('_',' ').title()}</b>
                <span class="alert-time">{e['start_time']} → {e['end_time']}</span>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<div style='color:#8A8270; font-size:13px;'>No abiotic stress events for this batch.</div>",
                    unsafe_allow_html=True)
    card_close()


def main():
    inject_css()
    page_header("Smart Mushroom Farm", "Batches",
                "Setup, growth stage, yield, and records — one place per batch.")

    batches = get_batches()
    batch_names = {f"{b['batch_code']} · {b['room_code']} ({b['status']})": b for b in batches}
    selected_name = st.selectbox("Select a batch", list(batch_names.keys()))
    batch = batch_names[selected_name]

    tab1, tab2, tab3 = st.tabs(["Overview & Phenology", "Yield & Efficiency", "Records"])
    with tab1:
        render_overview_tab(batch)
    with tab2:
        render_yield_tab(batch)
    with tab3:
        render_records_tab(batch)


if __name__ == "__main__":
    main()
