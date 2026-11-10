import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from thirsty import ui
from thirsty.estimator import (
    EstimateInput,
    estimate,
    households_equivalent,
    liters_to_gallons,
    stress_adjusted_liters,
)
from thirsty.states import STATES

cfg = ui.assumptions()
cooling = cfg["cooling_types"]
defaults = cfg["defaults"]
eq = cfg["equivalents"]

st.title("Water estimator")
st.caption("Annual water footprint of a data center: on-site cooling plus upstream power generation.")

stress = ui.water_stress()

# ---- Inputs --------------------------------------------------------------- #
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        capacity = st.number_input("IT capacity (MW)", min_value=1.0, max_value=5000.0, value=100.0, step=10.0)
        utilization = st.slider("Average utilization", 0.1, 1.0, float(defaults["utilization"]), 0.05,
                                help="Average IT load as a share of capacity.")
    with c2:
        cooling_key = st.selectbox("Cooling technology", list(cooling), format_func=lambda k: cooling[k]["label"])
        ct = cooling[cooling_key]
        wue = st.slider("Site WUE (L/kWh)", 0.0, 3.0, float(ct["site_wue_l_per_kwh"]), 0.05,
                        help=f"Typical range for this technology: {ct['range'][0]}-{ct['range'][1]} L/kWh. {ct['note']}")
    with c3:
        pue = st.slider("PUE", 1.05, 2.0, float(defaults["pue_by_cooling"][cooling_key]), 0.05,
                        help="Power Usage Effectiveness: total facility energy / IT energy.")
        grid = st.slider("Grid water intensity (L/kWh)", 0.0, 15.0,
                         float(defaults["grid_water_intensity_l_per_kwh"]), 0.1,
                         help=defaults["grid_water_intensity_note"])
    state = st.selectbox("Location (state)", ["- not specified -", *STATES])

result = estimate(EstimateInput(capacity, utilization, pue, wue, grid))

score = None
if state != "- not specified -" and stress is not None:
    row = stress.loc[stress["state"] == STATES[state]]
    if not row.empty:
        score = float(row["bws_score"].iloc[0])
        label = row["bws_label"].iloc[0]

# ---- Results -------------------------------------------------------------- #
total = result.total_water_l
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total water / year", f"{total / 1e9:,.2f} bn L", f"{liters_to_gallons(total) / 1e6:,.0f} M gallons",
          delta_color="off")
m2.metric("Direct (cooling)", f"{result.direct_water_l / 1e9:,.2f} bn L")
m3.metric("Indirect (power plants)", f"{result.indirect_water_l / 1e9:,.2f} bn L",
          f"{result.indirect_share:.0%} of total", delta_color="off")
m4.metric("US households equivalent", f"{households_equivalent(total, eq['household_liters_per_year']):,.0f}",
          help=eq["household_note"])

if score is not None:
    adjusted = stress_adjusted_liters(total, score)
    st.markdown(
        f"**{state}** has an Aqueduct baseline water stress of **{score:.2f} / 5 ({label})**. "
        f"Weighted by local scarcity, this footprint counts like **{adjusted / 1e9:,.2f} bn L** "
        "at an average-stress site."
    )
elif state != "- not specified -":
    st.caption("No water stress data loaded for this state yet.")

# ---- Cooling comparison --------------------------------------------------- #
st.markdown("### Same site, different cooling")
st.caption("Holding capacity, utilization and grid constant, using each technology's default WUE and PUE.")

rows = []
for key, c in cooling.items():
    r = estimate(EstimateInput(capacity, utilization, defaults["pue_by_cooling"][key],
                               c["site_wue_l_per_kwh"], grid))
    rows.append({"Cooling": c["label"], "Direct": r.direct_water_l / 1e9, "Indirect": r.indirect_water_l / 1e9,
                 "Energy (GWh)": r.facility_energy_kwh / 1e6})
comp = pd.DataFrame(rows)

fig = go.Figure()
fig.add_bar(name="Direct (cooling)", x=comp["Cooling"], y=comp["Direct"], marker_color=ui.DIRECT_COLOR)
fig.add_bar(name="Indirect (power plants)", x=comp["Cooling"], y=comp["Indirect"], marker_color=ui.INDIRECT_COLOR)
fig.update_layout(barmode="stack", yaxis_title="Billion litres per year", height=380,
                  margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=1.1),
                  paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)

st.markdown(
    "Air-cooled designs use almost no water on site, but their higher energy use moves "
    "water consumption upstream to power plants. The trade-off depends on the grid: on a "
    "wind- and solar-heavy grid (low grid water intensity), dry cooling wins clearly; on a "
    "water-intensive grid the gap closes, and dry cooling can even end up with the larger "
    "total footprint. Try moving the grid slider."
)

with st.expander("How this is calculated"):
    st.markdown(
        f"""
| Step | Formula | Value |
|---|---|---|
| IT energy | capacity × 8,760 h × utilization | {result.it_energy_kwh / 1e6:,.0f} GWh |
| Facility energy | IT energy × PUE | {result.facility_energy_kwh / 1e6:,.0f} GWh |
| Direct water | IT energy × site WUE | {result.direct_water_l / 1e9:,.2f} bn L |
| Indirect water | facility energy × grid water intensity | {result.indirect_water_l / 1e9:,.2f} bn L |

All assumptions live in `config/assumptions.yaml` with their sources.
"""
    )

ui.footer()
