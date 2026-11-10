"""Thirsty Compute - where is AI thirsty?

Run with:  streamlit run app.py
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

st.set_page_config(
    page_title="Thirsty Compute",
    page_icon=":material/water_drop:",
    layout="wide",
)

pages = [
    st.Page("views/overview.py", title="Overview", icon=":material/water_drop:", default=True),
    st.Page("views/map.py", title="Water risk map", icon=":material/map:"),
    st.Page("views/estimator.py", title="Water estimator", icon=":material/calculate:"),
    st.Page("views/insights.py", title="Insights", icon=":material/insights:"),
    st.Page("views/methodology.py", title="Methodology", icon=":material/menu_book:"),
]

st.navigation(pages).run()
