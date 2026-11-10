import streamlit as st

from thirsty import ui

HIGH_STRESS = {"High (40-80%)", "Extremely High (>80%)"}

st.title("Thirsty Compute")
st.subheader("Where is AI thirsty?")

st.markdown(
    """
The AI boom is a data center boom, and data centers need water: directly, to cool
servers, and indirectly, through the power plants that feed them. That water is
drawn from local watersheds, some of which are already under severe stress.

**Thirsty Compute** puts two public datasets on one map, mapped US data centers and
WRI's Aqueduct water stress scores, and adds a transparent estimator for the water
footprint of a planned facility.
"""
)

summary = ui.summary()
dcs = ui.datacenters()
stress = ui.water_stress()

c1, c2, c3 = st.columns(3)
if dcs is not None:
    c1.metric("Mapped US data centers", f"{len(dcs):,}")
    c2.metric("States covered", int((summary["datacenters"] > 0).sum()))
else:
    c1.metric("Mapped US data centers", "-")
    c2.metric("States covered", "-")

if dcs is not None and stress is not None:
    mapped = summary[summary["datacenters"] > 0]
    share = mapped.loc[mapped["bws_label"].isin(HIGH_STRESS), "datacenters"].sum() / mapped["datacenters"].sum()
    c3.metric("In high / extremely high water-stress states", f"{share:.0%}",
              help="Share of mapped data centers located in states whose Aqueduct baseline "
                   "water stress is High or Extremely High (state-level average).")
else:
    c3.metric("In high water-stress states", "-")

if dcs is None or stress is None:
    ui.missing_data_notice("Public datasets")

st.markdown("### Explore")
a, b, c = st.columns(3)
with a:
    st.markdown("**Water risk map**  \nData centers on top of state-level water stress, today and in 2030/2050 scenarios.")
    st.page_link("views/map.py", label="Open the map", icon=":material/map:")
with b:
    st.markdown("**Water estimator**  \nCapacity, cooling and location in, annual direct and indirect water out.")
    st.page_link("views/estimator.py", label="Estimate a site", icon=":material/calculate:")
with c:
    st.markdown("**Insights**  \nWhich states combine many data centers with scarce water?")
    st.page_link("views/insights.py", label="See the ranking", icon=":material/insights:")

st.markdown("### Why indirect water matters")
st.markdown(
    """
Most public discussion focuses on cooling water. But every kWh a data center draws
also consumes water at the power plant. Depending on the grid mix, that upstream share
can be several times larger than on-site use, which is why the estimator always shows both.
A low on-site WUE does not mean a low total water footprint.
"""
)

ui.footer()
