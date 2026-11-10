"""Shared Streamlit helpers: cached loaders and consistent notices."""

from __future__ import annotations

import streamlit as st

from . import data

STRESS_COLORSCALE = [
    [0.0, "#ffffb2"], [0.2, "#fed976"], [0.4, "#feb24c"],
    [0.6, "#fd8d3c"], [0.8, "#f03b20"], [1.0, "#bd0026"],
]
DIRECT_COLOR = "#1f77b4"
INDIRECT_COLOR = "#9ecae1"


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
