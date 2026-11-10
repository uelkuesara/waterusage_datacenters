import pytest

from thirsty.estimator import (
    EstimateInput,
    estimate,
    households_equivalent,
    liters_to_gallons,
    stress_adjusted_liters,
    stress_label,
)

BANDS = [[0, 1, "Low"], [1, 2, "Low-Medium"], [2, 3, "Medium-High"], [3, 4, "High"], [4, 5.01, "Extremely High"]]


def test_energy_and_water_math():
    r = estimate(EstimateInput(capacity_mw=1, utilization=1, pue=1.5,
                               site_wue_l_per_kwh=2.0, grid_water_intensity_l_per_kwh=4.0))
    assert r.it_energy_kwh == 8_760_000
    assert r.facility_energy_kwh == pytest.approx(13_140_000)
    assert r.direct_water_l == pytest.approx(17_520_000)
    assert r.indirect_water_l == pytest.approx(52_560_000)
    assert r.total_water_l == pytest.approx(70_080_000)
    assert r.indirect_share == pytest.approx(0.75)


def test_zero_grid_means_no_indirect():
    r = estimate(EstimateInput(10, 0.5, 1.2, 1.8, 0.0))
    assert r.indirect_water_l == 0
    assert r.indirect_share == 0


@pytest.mark.parametrize("kwargs", [
    dict(capacity_mw=0, utilization=0.5, pue=1.2, site_wue_l_per_kwh=1, grid_water_intensity_l_per_kwh=1),
    dict(capacity_mw=1, utilization=1.5, pue=1.2, site_wue_l_per_kwh=1, grid_water_intensity_l_per_kwh=1),
    dict(capacity_mw=1, utilization=0.5, pue=0.9, site_wue_l_per_kwh=1, grid_water_intensity_l_per_kwh=1),
    dict(capacity_mw=1, utilization=0.5, pue=1.2, site_wue_l_per_kwh=-1, grid_water_intensity_l_per_kwh=1),
])
def test_invalid_inputs_raise(kwargs):
    with pytest.raises(ValueError):
        estimate(EstimateInput(**kwargs))


def test_dry_cooling_can_lose_on_water_intensive_grid():
    """Documents the trade-off shown in the app."""
    evap = estimate(EstimateInput(100, 0.7, 1.3, 1.8, 12.0)).total_water_l
    dry = estimate(EstimateInput(100, 0.7, 1.5, 0.1, 12.0)).total_water_l
    assert dry > evap
    evap_clean = estimate(EstimateInput(100, 0.7, 1.3, 1.8, 1.0)).total_water_l
    dry_clean = estimate(EstimateInput(100, 0.7, 1.5, 0.1, 1.0)).total_water_l
    assert dry_clean < evap_clean


def test_conversions():
    assert liters_to_gallons(3.785411784) == pytest.approx(1)
    assert households_equivalent(828_000, 414_000) == 2


def test_stress_label_and_weighting():
    assert stress_label(4.2, BANDS) == "Extremely High"
    assert stress_label(0.5, BANDS) == "Low"
    assert stress_label(-1, BANDS) == "Arid & low water use"
    assert stress_label(float("nan"), BANDS) == "No data"
    assert stress_adjusted_liters(100, 2.5) == pytest.approx(100)
    assert stress_adjusted_liters(100, 5) == pytest.approx(200)
    assert stress_adjusted_liters(100, None) == 100
