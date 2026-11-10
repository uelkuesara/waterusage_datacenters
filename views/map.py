import plotly.graph_objects as go
import streamlit as st

from thirsty import ui

st.title("Water risk map")
st.caption("Mapped data centers on top of WRI Aqueduct baseline water stress (state level).")

dcs = ui.datacenters()
stress = ui.water_stress()
summary = ui.summary()

if dcs is None and stress is None:
    ui.missing_data_notice("Public datasets")
    st.stop()

# ---- Controls ------------------------------------------------------------- #
scenario_cols = sorted(c for c in summary.columns if c.startswith("bws_20"))
options = {"Today (baseline)": "bws_score"}
for col in scenario_cols:
    _, year, scen = col.split("_")
    options[f"{year} · {dict(bau='business as usual', opt='optimistic', pes='pessimistic').get(scen, scen)}"] = col

left, right = st.columns([2, 1])
with left:
    view = st.selectbox("Water stress", list(options), disabled=stress is None)
with right:
    show_points = st.toggle("Show data centers", value=dcs is not None, disabled=dcs is None)

col = options[view]
fig = go.Figure()

if stress is not None and col in summary:
    hover = summary["bws_label"] if col == "bws_score" else summary[col].round(2).astype(str)
    fig.add_trace(go.Choropleth(
        locations=summary["state"],
        z=summary[col].clip(lower=0),
        locationmode="USA-states",
        zmin=0, zmax=5,
        colorscale=ui.STRESS_COLORSCALE,
        colorbar=dict(title="Water stress<br>(0-5)", thickness=12),
        customdata=list(zip(summary["state_name"], hover, summary["datacenters"])),
        hovertemplate="<b>%{customdata[0]}</b><br>Water stress: %{z:.2f} (%{customdata[1]})"
                      "<br>Mapped data centers: %{customdata[2]}<extra></extra>",
        marker_line_color="white",
        marker_line_width=0.6,
    ))
elif stress is None:
    st.warning("Water stress data not loaded - showing data center locations only.")

if show_points and dcs is not None:
    names = dcs["name"].fillna("Unnamed data center")
    ops = dcs["operator"].fillna("unknown operator")
    fig.add_trace(go.Scattergeo(
        lon=dcs["lon"], lat=dcs["lat"],
        mode="markers",
        marker=dict(size=4, color="#08306b", opacity=0.7),
        text=names + "<br>" + ops,
        hovertemplate="%{text}<extra></extra>",
        name="Data centers",
    ))

fig.update_layout(
    geo=dict(scope="usa", projection_type="albers usa", showlakes=False, bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=0, r=0, t=0, b=0),
    height=560,
    showlegend=False,
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Water stress = ratio of water demand to renewable supply (Aqueduct 4.0), aggregated "
    "from sub-basins to states. State averages hide local hotspots: a data center can sit "
    "in a stressed basin inside a low-stress state. OpenStreetMap coverage is strongest in "
    "major markets and incomplete for smaller facilities."
)

ui.footer()
