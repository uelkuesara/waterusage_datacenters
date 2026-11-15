import streamlit as st

from thirsty import risk_map, ui

st.title("Water risk map")
st.caption("Mapped data centers on top of WRI Aqueduct baseline water stress (state level).")

dcs = ui.datacenters()
stress = ui.water_stress()
summary = ui.summary()

if dcs is None and stress is None:
    ui.missing_data_notice("Public datasets")
    st.stop()

if stress is None:
    st.warning("Water stress data not loaded - showing data center locations only.")

risk_map.render(summary, dcs)
st.caption(
    "Click a state to fly to it · ⌘/Ctrl + scroll or pinch to zoom · drag to pan · ↺ to reset."
)

st.caption(
    "Water stress = ratio of water demand to renewable supply (Aqueduct 4.0), aggregated "
    "from sub-basins to states. State averages hide local hotspots: a data center can sit "
    "in a stressed basin inside a low-stress state. OpenStreetMap coverage is strongest in "
    "major markets and incomplete for smaller facilities."
)

ui.footer()
