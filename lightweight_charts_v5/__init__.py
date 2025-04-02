# __init__.py

import os
import socket
from typing import List, Dict, Any, Optional, Union
import streamlit.components.v1 as components

COMPONENT_NAME = "lightweight_charts_v5_component"
__version__ = "0.1.3"
_RELEASE = True  # Keep this False for development flexibility

# Function to check if dev server is running
def _is_dev_server_running():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Set a short timeout to avoid hanging
        s.settimeout(0.5)
        s.connect(('localhost', 3001))
        # Try to receive data to confirm it's actually the dev server
        data = s.recv(1024)
        s.close()
        return len(data) > 0
    except:
        return False

# Use dev server if it's running and we're in dev mode, otherwise use build
if not _RELEASE and _is_dev_server_running():
    _component_func = components.declare_component(
        COMPONENT_NAME,
        url="http://localhost:3001",
    )
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
            default=default_value
        )