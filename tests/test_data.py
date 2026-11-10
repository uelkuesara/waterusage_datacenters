from pathlib import Path

import pandas as pd

from thirsty.data import parse_aqueduct_provincial, parse_overpass, state_summary

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_overpass_assigns_states_and_dedupes():
    payload = {"elements": [
        {"type": "area", "id": 1, "tags": {"ISO3166-2": "US-VA", "name": "Virginia"}},
        {"type": "node", "id": 10, "lat": 39.0, "lon": -77.5, "tags": {"name": "DC A", "operator": "Op1"}},
        {"type": "way", "id": 11, "center": {"lat": 39.1, "lon": -77.4}, "tags": {"building": "data_center"}},
        {"type": "node", "id": 10, "lat": 39.0, "lon": -77.5, "tags": {"name": "DC A"}},  # duplicate
        {"type": "area", "id": 2, "tags": {"ISO3166-2": "US-AZ"}},
        {"type": "node", "id": 12, "lat": 33.4, "lon": -112.0, "tags": {"brand": "Op2"}},
        {"type": "node", "id": 13, "tags": {}},  # no coordinates
    ]}
    df = parse_overpass(payload)
    assert len(df) == 3
    assert df["state"].tolist() == ["VA", "VA", "AZ"]
    assert df.loc[2, "operator"] == "Op2"


def test_parse_aqueduct_long_format():
    df = parse_aqueduct_provincial(FIXTURES / "aqueduct_provincial_sample.csv")
    assert set(df["state"]) == {"AZ", "VA"}
    assert df.loc[df["state"] == "AZ", "bws_score"].iloc[0] == 4.6


def test_state_summary_merges_counts_and_stress():
    dcs = pd.DataFrame({"state": ["VA", "VA", "AZ"], "lat": [1, 2, 3], "lon": [1, 2, 3]})
    stress = pd.DataFrame({"state": ["VA", "AZ"], "bws_score": [1.2, 4.6], "bws_label": ["a", "b"]})
    s = state_summary(dcs, stress)
    assert len(s) == 51
    assert s.loc[s["state"] == "VA", "datacenters"].iloc[0] == 2
    assert s.loc[s["state"] == "TX", "datacenters"].iloc[0] == 0
