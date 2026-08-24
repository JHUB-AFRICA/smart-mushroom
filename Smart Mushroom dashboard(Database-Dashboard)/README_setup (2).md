# Setup — what to do before this looks right

## 1. Add your mushroom photo
Create `assets/mushroom_hero.jpg` with a close-up photo of white button mushrooms
(light background, decent contrast on the left where the Home greeting sits).
Free sources: unsplash.com or pexels.com. If skipped, Home still renders fine as a
solid soil-brown gradient.

## 2. Wire in real data
Every mock function is named after the real MySQL table/columns it will eventually
query (see the docstring/comments at the top of each function) so the swap is a
straight function-body replacement once the database team loads real data:

- `Home.py` → sensor_readings, phenology_events, alerts
- `pages/1_Live_Monitoring.py` → rooms, sensor_readings, actuator_status_log, images
- `pages/2_Batches.py` → batches, phenology_events, yield_records, contamination_records,
  abiotic_stress_events
- `pages/3_Graphs.py` → sensor_readings (joined with sensors)
- `pages/4_Settings.py` → system_settings, sensors

## Project structure
```
Home.py                        # Overview: hero, live stats, system health, grow cycle, power, trend, alerts
theme.py                       # Shared CSS + component builders — import this in every page
pages/
  1_Live_Monitoring.py         # Room/rack grid, actuator status, camera snapshot + gallery, drill-down
  2_Batches.py                 # Tabs: Overview & Phenology · Yield & Efficiency · Records
  3_Graphs.py                  # Variable/room filters, single-room or compare view, CSV export
  4_Settings.py                # Alert thresholds + sensor metadata table
assets/
  mushroom_hero.jpg            # ← add this yourself (see above)
```

## Running it
```
pip install streamlit plotly pandas
streamlit run Home.py
```
Streamlit auto-builds the sidebar nav from the `pages/` folder. Numeric prefixes
(1_, 2_, 3_, 4_) control the nav order.

## What maps to what in the BRIDGE-AI doc
- **Grow-cycle stepper** (Home) + **phenology timeline** (Batches) → Section 3.4
- **Actuator status + camera gallery** (Live Monitoring) → Sections 1.2 / 3.3
- **Yield & Biological Efficiency** (Batches) → Section 5.1 — BE% is calculated live,
  never stored, so it can't go stale
- **Contamination + abiotic stress records** (Batches) → Section 4.4
- **CSV export** (Graphs) → Section 6, "manual Excel/CSV export" requirement
- **Sensor metadata table** (Settings) → Section 6, sensor/device IDs

## Known gap (intentionally left visible, not hidden)
The `sensors` table your database team built has `connectivity` but not `power`
(mains/battery/solar). Settings shows a note about this rather than inventing data —
worth raising with Charles's team if you want that column added.

## Bug fixed during review
The growth gallery on Live Monitoring was previously hardcoded to always show the
first room's batch photos, regardless of which room you selected in the drill-down.
Fixed so it now follows your selection.
