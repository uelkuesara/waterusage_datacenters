"""Shared Streamlit helpers: cached loaders and consistent notices."""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

from . import data

# Calm water (deep teal) -> stressed (amber) -> critical (red).
STRESS_COLORS = ["#0c2a2b", "#14605a", "#2fb9a0", "#e9c46a", "#f2843a", "#ff3d5a"]
STRESS_COLORSCALE = [[i / 5, c] for i, c in enumerate(STRESS_COLORS)]
DIRECT_COLOR = "#4fe3c1"
INDIRECT_COLOR = "#1d6f66"

# Plotly look shared by every chart: transparent, mono ticks, faint teal grid.
pio.templates["thirsty"] = go.layout.Template(layout=dict(
    font=dict(family="Montserrat, sans-serif", color="#cfeee8", size=13),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    colorway=["#4fe3c1", "#1d6f66", "#e9c46a", "#ff3d5a", "#3ab8ff"],
    xaxis=dict(gridcolor="rgba(79,227,193,.10)", zerolinecolor="rgba(79,227,193,.25)",
               tickfont=dict(family="Share Tech Mono, monospace", color="#8fb5ad", size=11)),
    yaxis=dict(gridcolor="rgba(79,227,193,.10)", zerolinecolor="rgba(79,227,193,.25)",
               tickfont=dict(family="Share Tech Mono, monospace", color="#8fb5ad", size=11)),
    hoverlabel=dict(bgcolor="#061214", bordercolor="#4fe3c1",
                    font=dict(family="Share Tech Mono, monospace", color="#e8fffb")),
))
pio.templates.default = "plotly_dark+thirsty"


@st.cache_data(show_spinner=False)
def assumptions() -> dict:
    return data.load_assumptions()


# The data folder is part of each cache key, so switching THIRSTY_DATA_DIR never
# serves stale data.
@st.cache_data(show_spinner="Loading data centers...")
def _datacenters(folder: str):
    return data.load_datacenters()


@st.cache_data(show_spinner="Loading water stress...")
def _water_stress(folder: str):
    return data.load_water_stress()


def datacenters():
    return _datacenters(str(data.data_dir()))


def water_stress():
    return _water_stress(str(data.data_dir()))


def summary():
    return data.state_summary(datacenters(), water_stress())


def missing_data_notice(what: str) -> None:
    st.info(
        f"**{what} not loaded yet.** Run `python scripts/fetch_data.py` once to download "
        "the public datasets, then reload this page.",
        icon=":material/download:",
    )


def footer() -> None:
    st.divider()
    st.caption(
        "Data: data center locations © OpenStreetMap contributors (ODbL) · "
        "Water stress: WRI Aqueduct 4.0 (CC BY 4.0) · Estimates are transparent, "
        "assumption-based approximations, not measurements."
    )
