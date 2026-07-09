"""Deterministic multi-pane app used by the e2e smoke test.

No network or data dependencies: candlesticks + moving-average overlay in
the top pane, colored volume histogram in the bottom pane.
"""
import math

import streamlit as st
from lightweight_charts_v5 import lightweight_charts_v5_component

st.set_page_config(layout="wide")


def make_data(n=120):
    candles, ma, volume = [], [], []
    price = 100.0
    for i in range(n):
        day = f"2024-{(i // 28) + 1:02d}-{(i % 28) + 1:02d}"
        delta = 2.5 * math.sin(i / 7.0) + 1.2 * math.cos(i / 3.0)
        o = price
        c = price + delta
        h = max(o, c) + 0.8
        l = min(o, c) - 0.8
        candles.append({"time": day, "open": o, "high": h, "low": l, "close": c})
        ma.append({"time": day, "value": 100.0 + 10.0 * math.sin(i / 15.0)})
        volume.append({
            "time": day,
            "value": 1000 + 500 * math.sin(i / 5.0) ** 2,
            "color": "#26a69a" if c >= o else "#ef5350",
        })
        price = c
    return candles, ma, volume


candles, ma, volume = make_data()

st.title("Smoke test chart")

lightweight_charts_v5_component(
    name="Smoke",
    charts=[
        {
            "chart": {"layout": {"background": {"color": "#FFFFFF"}}},
            "series": [
                {"type": "Candlestick", "data": candles, "options": {}},
                {"type": "Line", "data": ma, "options": {"color": "#2962FF", "lineWidth": 2}},
            ],
            "height": 400,
        },
        {
            "chart": {"layout": {"background": {"color": "#FFFFFF"}}},
            "series": [{"type": "Histogram", "data": volume, "options": {}}],
            "height": 150,
        },
    ],
    height=550,
    key="smoke_chart",
)
