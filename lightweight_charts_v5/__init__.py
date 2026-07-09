# __init__.py

import os
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _dist_version
from typing import List, Dict, Any, Optional, Union
import streamlit.components.v1 as components

COMPONENT_NAME = "lightweight_charts_v5_component"

try:
    __version__ = _dist_version("streamlit-lightweight-charts-v5")
except PackageNotFoundError:
    # Source checkout that was never pip-installed
    __version__ = "0.0.0+dev"

# Loading the frontend from the Vite dev server (npm start, port 3001) is an
# explicit opt-in so that installed releases never touch the network:
#   LWC_V5_DEV_SERVER=1                  -> http://localhost:3001
#   LWC_V5_DEV_SERVER=http://host:port   -> custom dev server URL
_dev_server = os.environ.get("LWC_V5_DEV_SERVER", "")
if _dev_server.lower() in ("1", "true", "yes"):
    _dev_server = "http://localhost:3001"

if _dev_server:
    _component_func = components.declare_component(COMPONENT_NAME, url=_dev_server)
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component(COMPONENT_NAME, path=build_dir)

def lightweight_charts_v5_component(name, data=None, 
                                    charts=None, 
                                    height: int = 400, 
                                    take_screenshot: bool = False, 
                                    zoom_level: int = 200, 
                                    fonts: List[str] = None,
                                    configure_time_scale: bool = False,
                                    key=None):
    """
    Create a new instance of the component.

    Parameters
    ----------
    name: str
        A label or title.
    data: list of dict
        Data for a single pane chart (if not using multiple panes).
    charts: list of dict
        A list of pane configuration dictionaries (for multiple panes).

        Each series in a chart can include rectangles with the following format:
        {
            "startTime": "2023-01-01",  # Time for the starting point
            "startPrice": 100.0,        # Price for the starting point
            "endTime": "2023-01-15",    # Time for the ending point
            "endPrice": 120.0,          # Price for the ending point
            "fillColor": "rgba(255, 0, 0, 0.2)",  # Fill color with opacity
            "borderColor": "rgba(255, 0, 0, 1)",  # Optional border color
            "borderWidth": 1,           # Optional border width
            "opacity": 0.5              # Optional opacity (overrides the one in fillColor)
        }

    height: int
        Overall chart height (if using single pane or as a fallback).
    take_screenshot: bool
        If True, triggers a screenshot of the chart
    zoom_level: int
        Number of bars to show in the initial view (default: 200).
    fonts: List[str]
        List of optional google fonts that will be downloaded for use.
    configure_time_scale: bool
        If True, applies additional time scale configuration that helps with 
        multi-chart layouts with really small charts but may cause issues with 
        screenshot functionality. Default is False.
    key: str or None
        Optional key.

    Returns
    -------
    dict or int
        If take_screenshot is True, returns a dict containing the screenshot data.
        Otherwise returns the component's default return value (int).
    """
    # Use different defaults based on screenshot mode
    default_value = None if take_screenshot else 0

    # If charts configuration is provided, pass that.
    # Otherwise, pass data and height.
    if charts is not None:
        return _component_func(
            name=name,
            charts=charts,
            height=height,
            take_screenshot=take_screenshot,
            zoom_level=zoom_level,
            fonts=fonts, 
            key=key,
            configure_time_scale=configure_time_scale,
            default=default_value
        )
    else:
        return _component_func(
            name=name,
            data=data,
            height=height,
            take_screenshot=take_screenshot,
            zoom_level=zoom_level,
            key=key,
            configure_time_scale=configure_time_scale,
            default=default_value
        )