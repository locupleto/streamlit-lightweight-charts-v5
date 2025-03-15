# Streamlit Lightweight Charts v5

A Streamlit component that integrates TradingView's Lightweight Charts v5 library, providing interactive financial charts with multi-pane support for technical analysis.

## Overview

Streamlit Lightweight Charts v5 is built around version 5 of the TradingView Lightweight Charts library, which introduces powerful multi-pane capabilities perfect for technical analysis. This component allows you to create great looking financial charts with multiple indicators stacked vertically, similar to popular trading platforms.

Key features:

- Multi-pane chart layouts for price and indicators
- Customizable themes and styles
- Add your own favourite standalone technical indicators (RSI, MACD, Williams %R etc.)
- Use overlay indicators (Moving Averages, AVWAP, Pivot Points...)
- Yield curve charts
- Supports Screenshots

![Screenshot](https://github.com/locupleto/streamlit-lightweight-charts-v5/raw/main/Screenshot.png)

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install streamlit-lightweight-charts-v5
pip install streamlit yfinance numpy  # for running demos
```

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
    {"time": str(date.date()), "value": float(row["Close"].iloc[0])}  
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

The repository includes a `demo/` directory with two example scripts that showcase how to use the component.

- `minimal_demo.py`: A minimal example using Yahoo Finance stock data
- `chart_demo.py`: A slightly more advanced example with multiple indicators
- `chart_themes.py`: Theme customization examples for the chart_demo module.
- `indicators.py`: Example indicators for the chart_demo module.
- `yield_curve.py`: Yield curve example chart for the chart_demo module.

You can find the demo files in the [GitHub repository](https://github.com/locupleto/streamlit-lightweight-charts-v5/tree/main/demo).

## Running the Demo Applications 

To test the two demo scripts, run them using **Streamlit**:

```bash
streamlit run demo/minimal_demo.py  # Minimal example
streamlit run demo/chart_demo.py    # Full demo with indicators
```

## License

This project is licensed under the MIT License.
