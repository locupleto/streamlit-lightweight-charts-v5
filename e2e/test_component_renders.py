from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from e2e_utils import StreamlitRunner

SMOKE_APP = Path(__file__).parent.absolute() / "smoke_app.py"


@pytest.fixture(autouse=True, scope="module")
def streamlit_app():
    with StreamlitRunner(SMOKE_APP) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    page.goto(streamlit_app.server_url)
    page.get_by_role("img", name="Running...").is_hidden()


def test_component_renders_chart_canvas(page: Page):
    """The component iframe mounts and lightweight-charts draws its canvases."""
    frame = page.frame_locator('iframe[title*="lightweight_charts_v5"]')
    # lightweight-charts renders one canvas pair per pane; the smoke app has
    # two panes, so at least two canvases must be attached and visible
    canvases = frame.locator("canvas")
    expect(canvases.first).to_be_visible(timeout=30_000)
    assert canvases.count() >= 2
