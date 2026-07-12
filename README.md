# Streamlit Lightweight Charts v5

A Streamlit component that integrates TradingView's Lightweight Charts v5 library, providing interactive financial charts with multi-pane support for technical analysis.

## Overview

Streamlit Lightweight Charts v5 is built around version 5 of the TradingView Lightweight Charts library, which introduces powerful multi-pane capabilities perfect for technical analysis. This component allows you to create great looking financial charts with multiple indicators stacked vertically, similar to popular trading platforms.

Key features:

- Multi-pane chart layouts for price and indicators
- Customizable themes and styles
- Add your own favourite standalone technical indicators (RSI, MACD, Williams %R etc.)
- Use overlay indicators (Moving Averages, AVWAP, Pivot Points...)
- Support for drawing Rectangles for e.g. Support / Resistance areas from code
- Volume Profile overlay with pivot-based horizontal volume distribution
- Ichimoku Cloud overlay with regime-colored kumo fill between the Senkou spans
- Yield curve charts
- Supports Screenshots

![Screenshot](https://github.com/locupleto/streamlit-lightweight-charts-v5/raw/main/Screenshot_1.png)

![Screenshot](https://github.com/locupleto/streamlit-lightweight-charts-v5/raw/main/Screenshot_2.png)

![Screenshot](https://github.com/locupleto/streamlit-lightweight-charts-v5/raw/main/Screenshot_3.png)

![Volume Profile](https://github.com/locupleto/streamlit-lightweight-charts-v5/raw/main/Screenshot_4.png)

![Ichimoku Cloud](https://github.com/locupleto/streamlit-lightweight-charts-v5/raw/main/Screenshot_5.png?v=2)

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install streamlit-lightweight-charts-v5
pip install yfinance>=1.0  # Required: v1.0+ to avoid rate limiting
```

**Note:** yfinance 1.0 or higher is required to avoid running into Yahoo Finance API rate limiting issues when running the demos.

## Quick Start

```python
import streamlit as st
from lightweight_charts_v5 import lightweight_charts_v5_component
import yfinance as yf

# Load stock data
ticker = "AAPL"
data = yf.download(ticker, period="100d", interval="1d", auto_adjust=False) 

# Convert data to Lightweight Charts format, ensuring values are proper floats
chart_data = [
    {"time": str(date.date()), "value": float(row["Close"])}
    for date, row in data.iterrows()
]

# Streamlit app
st.title(f"{ticker} Stock Price Line Chart")

# Render the chart
lightweight_charts_v5_component(
    name=f"{ticker} Chart",
    charts=[{
        "chart": {"layout": {"background": {"color": "#FFFFFF"}}},
        "series": [{
            "type": "Line",
            "data": chart_data,
            "options": {"color": "#2962FF"}
        }],
        "height": 400
    }],
    height=400
)
```

## Demos

The repository includes a `demo/` directory with example applications. There are two main entry points:

- `minimal_demo.py`: A minimal single-chart example using Yahoo Finance stock data — the best place to start
- `chart_demo.py`: The full-featured demo application. A **"Select Demo"** dropdown lets you switch between five demos: StockChart (candlesticks with technical indicators), Volume Profile, Ichimoku Cloud, Yield Curve, and Multi-Chart (a grid of charts)

```bash
streamlit run demo/minimal_demo.py   # Minimal example
streamlit run demo/chart_demo.py     # Full demo with dropdown selector
```

Two of the demos from the dropdown can also be run directly as standalone apps:

```bash
streamlit run demo/volume_profile_demo.py   # Volume profile overlay with configurable pivot detection, price bins, and value area
streamlit run demo/ichimoku_demo.py         # Ichimoku Cloud overlay with regime-colored kumo fill
```

The remaining files (`chart_themes.py`, `indicators.py`, `multi_demo.py`, `yield_curve.py`) are supporting modules imported by `chart_demo.py` and are not meant to be run directly.

See the [demo directory](https://github.com/locupleto/streamlit-lightweight-charts-v5/tree/main/demo) and its README for full details.

## License

This project is licensed under the MIT License.
