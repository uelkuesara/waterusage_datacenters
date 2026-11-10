import pandas as pd
import streamlit as st

from thirsty import ui

cfg = ui.assumptions()

st.title("Methodology")

st.markdown(
    """
### Model

| Quantity | Formula |
|---|---|
| IT energy (kWh/yr) | IT capacity (MW) × 1,000 × 8,760 h × utilization |
| Facility energy | IT energy × PUE |
| **Direct water** (on site) | IT energy × site WUE |
| **Indirect water** (upstream) | facility energy × grid water intensity |

*Site WUE* (Water Usage Effectiveness) follows The Green Grid definition: litres of water
consumed on site per kWh of IT energy. *Grid water intensity* is the water consumed at
power plants per kWh of electricity delivered.

**Stress weighting.** To compare sites, the estimator can weight litres by the Aqueduct
water stress score, normalised so that a score of 2.5 equals 1.0. It is a transparent
ranking heuristic, not a physical quantity.
"""
)

st.markdown("### Cooling assumptions")
rows = [{"Technology": c["label"], "Default WUE (L/kWh)": c["site_wue_l_per_kwh"],
         "Typical range": f"{c['range'][0]}-{c['range'][1]}",
         "Default PUE": cfg["defaults"]["pue_by_cooling"][k], "Note": c["note"]}
        for k, c in cfg["cooling_types"].items()]
st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

st.markdown(
    f"""
**Grid water intensity default:** {cfg['defaults']['grid_water_intensity_l_per_kwh']} L/kWh.
{cfg['defaults']['grid_water_intensity_note']}

**Household equivalent:** {cfg['equivalents']['household_liters_per_year']:,} L per year.
{cfg['equivalents']['household_note']}

All values live in `config/assumptions.yaml` and can be changed without touching code.

### Data sources

| Dataset | Publisher | Use | License |
|---|---|---|---|
| Data center locations (`telecom=data_center`, `building=data_center`) | OpenStreetMap contributors | Map points, counts per state | ODbL 1.0 |
| Aqueduct 4.0 Country & Provincial Rankings | World Resources Institute | Water stress per state, 2030/2050/2080 scenarios | CC BY 4.0 |
| United States Data Center Energy Usage Report (2016, 2024) | Lawrence Berkeley National Laboratory | WUE and grid water intensity defaults | Public report |
| WaterSense statistics | US EPA | Household equivalent | Public |

### Limitations

- **State averages hide hotspots.** Aqueduct is computed per sub-basin; aggregating to states
  smooths over local extremes. A basin-level overlay is the natural next step.
- **Locations are incomplete.** OpenStreetMap is community-edited; large markets are well
  covered, smaller facilities less so. Facilities are counted, not weighted by capacity.
- **One grid factor.** The indirect estimate uses a single grid water intensity per run.
  Real values vary by region, hour and power purchase agreements.
- **Consumption, not withdrawal.** Figures describe water consumed (evaporated or not returned),
  which is what matters for local scarcity.
"""
)

ui.footer()
