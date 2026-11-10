"""Download the public datasets and build the processed files the app reads.

Usage:
    python scripts/fetch_data.py            # both datasets
    python scripts/fetch_data.py --only osm
    python scripts/fetch_data.py --only aqueduct

Aqueduct: the script tries to download WRI's country-rankings zip. If that fails
(WRI may ask for a short form), download it manually from
https://www.wri.org/data/aqueduct-40-country-rankings and drop the .zip or .xlsx
into data/raw/. The script will pick it up.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from thirsty.data import (  # noqa: E402
    DATACENTERS_FILE,
    WATER_STRESS_FILE,
    fetch_osm_datacenters,
    parse_aqueduct_provincial,
)

RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
AQUEDUCT_URL = "https://files.wri.org/aqueduct/aqueduct-4-0-country-rankings.zip"


def build_osm() -> None:
    print("Querying OpenStreetMap (Overpass) for US data centers - this can take a few minutes...")
    df = fetch_osm_datacenters()
    out = PROCESSED / DATACENTERS_FILE
    df.to_csv(out, index=False)
    print(f"  {len(df):,} data centers, {df['state'].notna().mean():.0%} with a state -> {out}")


def _download_aqueduct() -> Path | None:
    import requests

    target = RAW / "aqueduct-4-0-country-rankings.zip"
    try:
        print(f"Downloading Aqueduct 4.0 country rankings from {AQUEDUCT_URL} ...")
        with requests.get(AQUEDUCT_URL, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(target, "wb") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
        return target
    except Exception as exc:  # noqa: BLE001
        print(f"  Download failed ({exc}).")
        return None


def _find_aqueduct_table() -> Path | None:
    for zpath in RAW.glob("*.zip"):
        with zipfile.ZipFile(zpath) as z:
            for name in z.namelist():
                if name.lower().endswith((".xlsx", ".csv")) and "__macosx" not in name.lower():
                    z.extract(name, RAW / zpath.stem)
    candidates = [p for p in RAW.rglob("*") if p.suffix.lower() in {".xlsx", ".csv"}]
    # Prefer files whose name mentions provinces / admin level 1
    candidates.sort(key=lambda p: ("prov" not in p.name.lower(), len(p.name)))
    return candidates[0] if candidates else None


def build_aqueduct() -> None:
    table = _find_aqueduct_table()
    if table is None and _download_aqueduct():
        table = _find_aqueduct_table()
    if table is None:
        sys.exit(
            "No Aqueduct file found. Download the country rankings from "
            "https://www.wri.org/data/aqueduct-40-country-rankings and place it in data/raw/."
        )
    errors = []
    for candidate in [table, *[p for p in RAW.rglob("*") if p.suffix.lower() in {".xlsx", ".csv"} and p != table]]:
        try:
            df = parse_aqueduct_provincial(candidate)
            break
        except ValueError as exc:
            errors.append(str(exc))
    else:
        sys.exit("Could not parse any Aqueduct file:\n" + "\n".join(errors))
    out = PROCESSED / WATER_STRESS_FILE
    df.to_csv(out, index=False)
    print(f"  {len(df)} states with water stress scores -> {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", choices=["osm", "aqueduct"])
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    if args.only in (None, "aqueduct"):
        build_aqueduct()
    if args.only in (None, "osm"):
        build_osm()
    print("Done. Start the app with: streamlit run app.py")


if __name__ == "__main__":
    main()
