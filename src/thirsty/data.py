"""Loading and preparing the public datasets.

Two processed files power the app (created by `scripts/fetch_data.py`):

* data/processed/datacenters_us.csv    - data center locations (OpenStreetMap, ODbL)
* data/processed/water_stress_states.csv - Aqueduct 4.0 water stress per state (WRI, CC BY 4.0)

Set THIRSTY_DATA_DIR to point the app at another folder (used by the tests).
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import yaml

from .estimator import stress_label
from .states import CODE_TO_NAME, to_code

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "assumptions.yaml"

DATACENTERS_FILE = "datacenters_us.csv"
WATER_STRESS_FILE = "water_stress_states.csv"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# One query: for every US state, emit the state area followed by the data centers inside it.
OVERPASS_QUERY = """
[out:json][timeout:300];
area["ISO3166-1"="US"][admin_level=2]->.us;
rel(area.us)["admin_level"="4"]["ISO3166-2"~"^US-"];
map_to_area->.states;
foreach.states->.s(
  .s out tags;
  (
    nwr(area.s)["telecom"="data_center"];
    nwr(area.s)["building"="data_center"];
  );
  out center tags;
);
"""


def data_dir() -> Path:
    return Path(os.environ.get("THIRSTY_DATA_DIR", ROOT / "data" / "processed"))


def load_assumptions() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


# --------------------------------------------------------------------------- #
# Loading processed data (used by the app)
# --------------------------------------------------------------------------- #

def load_datacenters() -> pd.DataFrame | None:
    path = data_dir() / DATACENTERS_FILE
    if not path.exists():
        return None
    df = pd.read_csv(path)
    return df.dropna(subset=["lat", "lon"])


def load_water_stress() -> pd.DataFrame | None:
    path = data_dir() / WATER_STRESS_FILE
    if not path.exists():
        return None
    df = pd.read_csv(path)
    bands = load_assumptions()["water_stress_labels"]
    df["bws_label"] = df["bws_score"].apply(lambda s: stress_label(s, bands))
    return df


def state_summary(dcs: pd.DataFrame | None, stress: pd.DataFrame | None) -> pd.DataFrame:
    """One row per state: number of mapped data centers and water stress."""
    base = pd.DataFrame({"state": list(CODE_TO_NAME), "state_name": list(CODE_TO_NAME.values())})
    if dcs is not None and len(dcs):
        counts = dcs.groupby("state").size().rename("datacenters").reset_index()
        base = base.merge(counts, on="state", how="left")
    else:
        base["datacenters"] = 0
    base["datacenters"] = base["datacenters"].fillna(0).astype(int)
    if stress is not None:
        keep = [c for c in stress.columns if c == "state" or c.startswith("bws")]
        base = base.merge(stress[keep], on="state", how="left")
    return base


# --------------------------------------------------------------------------- #
# Building processed data (used by scripts/fetch_data.py)
# --------------------------------------------------------------------------- #

def parse_overpass(payload: dict) -> pd.DataFrame:
    """Turn the Overpass response into one row per data center, tagged with its state."""
    rows, current_state, seen = [], None, set()
    for el in payload.get("elements", []):
        tags = el.get("tags", {})
        if el["type"] == "area":
            current_state = to_code(tags.get("ISO3166-2", "").replace("US-", ""))
            continue
        lat = el.get("lat", el.get("center", {}).get("lat"))
        lon = el.get("lon", el.get("center", {}).get("lon"))
        key = (el["type"], el["id"])
        if lat is None or lon is None or key in seen:
            continue
        seen.add(key)
        rows.append({
            "osm_id": f"{el['type']}/{el['id']}",
            "name": tags.get("name"),
            "operator": tags.get("operator") or tags.get("brand"),
            "lat": lat,
            "lon": lon,
            "state": current_state or to_code(tags.get("addr:state")),
            "city": tags.get("addr:city"),
        })
    return pd.DataFrame(rows, columns=["osm_id", "name", "operator", "lat", "lon", "state", "city"])


def fetch_osm_datacenters(timeout: int = 330) -> pd.DataFrame:
    import requests

    resp = requests.post(OVERPASS_URL, data={"data": OVERPASS_QUERY}, timeout=timeout,
                         headers={"User-Agent": "thirsty-compute (portfolio project)"})
    resp.raise_for_status()
    return parse_overpass(resp.json())


def _norm(col: str) -> str:
    return str(col).strip().lower()


def parse_aqueduct_provincial(path: Path) -> pd.DataFrame:
    """Extract US state water stress from the Aqueduct 4.0 country-rankings download.

    Accepts the Excel workbook or a CSV export. Handles the long format
    (indicator_name / weight / score columns) described in WRI's data dictionary.
    Returns columns: state, bws_score, plus bws_<year>_<scenario> when future
    projections are present.
    """
    frames = []
    if path.suffix.lower() in {".xlsx", ".xls"}:
        for _, sheet in pd.read_excel(path, sheet_name=None).items():
            frames.append(sheet)
    else:
        frames.append(pd.read_csv(path))

    baseline, future = None, []
    for df in frames:
        df = df.rename(columns={c: _norm(c) for c in df.columns})
        if "name_1" not in df.columns or "name_0" not in df.columns:
            continue  # country-level sheet or notes
        us = df[df["name_0"].astype(str).str.strip().isin(["United States", "United States of America"])]
        if us.empty:
            continue
        if "indicator_name" in us.columns:
            us = us[us["indicator_name"].astype(str).str.lower() == "bws"]
        if "weight" in us.columns:
            us = us[us["weight"].astype(str).str.lower().isin(["tot", "total"])]
        if "score" not in us.columns:
            continue
        us = us.assign(state=us["name_1"].map(to_code)).dropna(subset=["state"])
        if "year" in us.columns and "scenario" in us.columns:
            for (year, scen), grp in us.groupby(["year", "scenario"]):
                col = f"bws_{int(year)}_{str(scen).lower()}"
                future.append(grp[["state", "score"]].rename(columns={"score": col}))
        else:
            baseline = us[["state", "score"]].rename(columns={"score": "bws_score"})

    if baseline is None:
        raise ValueError(
            f"No US provincial baseline water stress found in {path.name}. "
            "Expected the Aqueduct 4.0 country rankings download (provincial baseline)."
        )
    out = baseline.groupby("state", as_index=False).mean(numeric_only=True)
    for f in future:
        out = out.merge(f.groupby("state", as_index=False).mean(numeric_only=True), on="state", how="left")
    return out
