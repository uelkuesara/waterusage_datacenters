import plotly.express as px
import streamlit as st

from thirsty import ui

st.title("Insights")
st.caption("Where do many data centers meet scarce water?")

dcs = ui.datacenters()
stress = ui.water_stress()
summary = ui.summary()

if dcs is None or stress is None:
    ui.missing_data_notice("Both datasets")
    st.stop()

mapped = summary[summary["datacenters"] > 0].copy()
high = mapped["bws_score"] >= 3
st.markdown(
    f"**{mapped.loc[high, 'datacenters'].sum():,} of {mapped['datacenters'].sum():,}** mapped data centers "
    f"({mapped.loc[high, 'datacenters'].sum() / mapped['datacenters'].sum():.0%}) are in states with "
    "**high or extremely high** baseline water stress."
)

# Exposure = number of facilities weighted by water stress. A simple, explainable ranking.
mapped["exposure"] = mapped["datacenters"] * mapped["bws_score"].clip(lower=0)
top = mapped.sort_values("exposure", ascending=False).head(10)

c1, c2 = st.columns(2)
with c1:
    st.markdown("#### Top 10 states by water-stress exposure")
    fig = px.bar(top.sort_values("exposure"), x="exposure", y="state_name", orientation="h",
                 color="bws_score", color_continuous_scale=ui.STRESS_COLORSCALE, range_color=[0, 5],
                 labels={"exposure": "Data centers × water stress", "state_name": "", "bws_score": "Stress"},
                 hover_data={"datacenters": True, "bws_label": True})
    fig.update_layout(height=420, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    st.markdown("#### Data centers vs. water stress")
    fig = px.scatter(mapped, x="bws_score", y="datacenters", text="state", size="datacenters",
                     color="bws_score", color_continuous_scale=ui.STRESS_COLORSCALE, range_color=[0, 5],
                     labels={"bws_score": "Baseline water stress (0-5)", "datacenters": "Mapped data centers"},
                     hover_name="state_name")
    fig.update_traces(textposition="top center", marker=dict(line=dict(width=0)))
    fig.update_layout(height=420, margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Top-right quadrant: large clusters in water-stressed states.")

st.markdown("#### All states")
table = mapped.sort_values("exposure", ascending=False)[
    ["state_name", "datacenters", "bws_score", "bws_label", "exposure"]
].rename(columns={"state_name": "State", "datacenters": "Data centers", "bws_score": "Water stress",
                  "bws_label": "Category", "exposure": "Exposure"})
st.dataframe(table, hide_index=True, use_container_width=True,
             column_config={"Water stress": st.column_config.NumberColumn(format="%.2f"),
                            "Exposure": st.column_config.NumberColumn(format="%.0f")})

st.caption(
    "Counts facilities, not capacity: a hyperscale campus and a small colocation site count the "
    "same. OpenStreetMap does not record capacity consistently, so a capacity-weighted view is a "
    "planned next step."
)

ui.footer()
