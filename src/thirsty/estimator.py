"""Water footprint estimator for a data center.

Pure functions, no I/O: easy to test and reuse outside the app.

Model
-----
IT energy (kWh/yr)        = capacity_mw * 1000 * 8760 * utilization
Facility energy (kWh/yr)  = IT energy * PUE
Direct (on-site) water    = IT energy * site WUE           (cooling)
Indirect (upstream) water = facility energy * grid water intensity  (power plants)

Site WUE follows The Green Grid definition (litres per kWh of IT energy).
"""

from __future__ import annotations

from dataclasses import dataclass

HOURS_PER_YEAR = 8760


@dataclass(frozen=True)
class EstimateInput:
    capacity_mw: float
    utilization: float
    pue: float
    site_wue_l_per_kwh: float
    grid_water_intensity_l_per_kwh: float

    def validate(self) -> None:
        if self.capacity_mw <= 0:
            raise ValueError("capacity_mw must be positive")
        if not 0 < self.utilization <= 1:
            raise ValueError("utilization must be in (0, 1]")
        if self.pue < 1:
            raise ValueError("PUE cannot be below 1.0")
        if self.site_wue_l_per_kwh < 0 or self.grid_water_intensity_l_per_kwh < 0:
            raise ValueError("water intensities cannot be negative")


@dataclass(frozen=True)
class EstimateResult:
    it_energy_kwh: float
    facility_energy_kwh: float
    direct_water_l: float
    indirect_water_l: float

    @property
    def total_water_l(self) -> float:
        return self.direct_water_l + self.indirect_water_l

    @property
    def indirect_share(self) -> float:
        total = self.total_water_l
        return self.indirect_water_l / total if total else 0.0


def estimate(inp: EstimateInput) -> EstimateResult:
    """Annual water footprint of a data center."""
    inp.validate()
    it_kwh = inp.capacity_mw * 1000 * HOURS_PER_YEAR * inp.utilization
    facility_kwh = it_kwh * inp.pue
    return EstimateResult(
        it_energy_kwh=it_kwh,
        facility_energy_kwh=facility_kwh,
        direct_water_l=it_kwh * inp.site_wue_l_per_kwh,
        indirect_water_l=facility_kwh * inp.grid_water_intensity_l_per_kwh,
    )


def liters_to_gallons(liters: float) -> float:
    return liters / 3.785411784


def households_equivalent(liters: float, household_liters_per_year: float) -> float:
    return liters / household_liters_per_year


def stress_label(score: float | None, bands: list[list]) -> str:
    """Map an Aqueduct water stress score (0-5) to its category label."""
    if score is None or score != score:  # None or NaN
        return "No data"
    if score < 0:
        return "Arid & low water use"  # Aqueduct uses -1 for this category
    for low, high, label in bands:
        if low <= score < high:
            return label
    return "No data"


def stress_adjusted_liters(liters: float, score: float | None) -> float:
    """Weight a volume by local scarcity: same litre counts more where water is scarce.

    Uses the Aqueduct score (0-5) as a simple linear multiplier normalised to the
    midpoint (score 2.5 -> factor 1.0). A transparent heuristic for ranking sites,
    not a physical quantity.
    """
    if score is None or score != score or score < 0:
        return liters
    return liters * (max(score, 0.1) / 2.5)
