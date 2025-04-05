from typing import List, Dict, Any

def get_sample_yield_curves() -> List[Dict[str, Any]]:
    """Returns sample yield curve data"""
    curve1 = [
        {"time": 1, "value": 5.378},
        {"time": 2, "value": 5.372},
        {"time": 3, "value": 5.271},
        {"time": 6, "value": 5.094},
        {"time": 12, "value": 4.739},
        {"time": 24, "value": 4.237},
        {"time": 36, "value": 4.036},
        {"time": 60, "value": 3.887},
        {"time": 84, "value": 3.921},
        {"time": 120, "value": 4.007},
        {"time": 240, "value": 4.366},
        {"time": 360, "value": 4.29},
    ]

    curve2 = [
        {"time": 1, "value": 5.381},
        {"time": 2, "value": 5.393},
        {"time": 3, "value": 5.425},
        {"time": 6, "value": 5.494},
        {"time": 12, "value": 5.377},
        {"time": 24, "value": 4.883},
        {"time": 36, "value": 4.554},
        {"time": 60, "value": 4.241},
        {"time": 84, "value": 4.172},
        {"time": 120, "value": 4.084},
        {"time": 240, "value": 4.365},
        {"time": 360, "value": 4.176},
    ]
    return [curve1, curve2]

def get_yield_curve_config(theme: dict) -> Dict[str, Any]:
    """Creates yield curve chart configuration"""
    curves = get_sample_yield_curves()

    # Extract title font settings from theme correctly
    title_font_family = theme.get("titleOptions", {}).get("fontFamily", "inherit")
    title_font_size = theme.get("titleOptions", {}).get("fontSize", 14)
    title_font_style = theme.get("titleOptions", {}).get("fontStyle", "normal")

    return {
        "chart": {
            "layout": theme["layout"],
            "grid": {
                "vertLines": {"visible": False},
                "horzLines": {"visible": False},
            },
            "yieldCurve": {
                "baseResolution": 12,
                "minimumTimeRange": 10,
                "startTimeRange": 3,
            },
            "handleScroll": False,
            "handleScale": False,
            "fontFamily": "inherit",
            "titleFontFamily": title_font_family,
            "titleFontSize": title_font_size,
            "titleFontStyle": title_font_style,
        },
        "series": [
            {
                "type": "Line",
                "data": curves[0],
                "options": {
                    "lineType": 2,
                    "color": "#26c6da",
                    "pointMarkersVisible": True,
                    "lineWidth": 2,
                }
            },
            {
                "type": "Line",
                "data": curves[1],
                "options": {
                    "lineType": 2,
                    "color": "rgb(164, 89, 209)",
                    "pointMarkersVisible": True,
                    "lineWidth": 1,
                }
            }
        ],
        "height": 400,
        "title": "Yield Curve Comparison",
    }