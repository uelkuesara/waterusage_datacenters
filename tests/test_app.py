"""Smoke tests: every page renders without exceptions, with and without data."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures" / "processed"
PAGES = ["views/overview.py", "views/map.py", "views/estimator.py", "views/insights.py", "views/methodology.py"]


@pytest.mark.parametrize("page", PAGES)
@pytest.mark.parametrize("with_data", [True, False])
def test_page_renders(page, with_data, monkeypatch, tmp_path):
    monkeypatch.setenv("THIRSTY_DATA_DIR", str(FIXTURES if with_data else tmp_path))
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    at.run()
    at.switch_page(page).run()
    assert not at.exception, at.exception


def test_estimator_reacts_to_state(monkeypatch):
    monkeypatch.setenv("THIRSTY_DATA_DIR", str(FIXTURES))
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    at.run()
    at.switch_page("views/estimator.py").run()
    at.selectbox[1].select("Arizona").run()
    assert not at.exception
    assert any("Arizona" in m.value and "4.60" in m.value for m in at.markdown)


def test_missing_data_shows_setup_hint(monkeypatch, tmp_path):
    monkeypatch.setenv("THIRSTY_DATA_DIR", str(tmp_path))
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    at.run()
    assert any("fetch_data.py" in i.value for i in at.info)
