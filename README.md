# Streamlit Lightweight Charts v5

A Streamlit component that integrates TradingView's Lightweight Charts v5 library, providing interactive financial charts with multi-pane support for technical analysis.

## Overview

Streamlit Lightweight Charts v5 is built around version 5 of the TradingView Lightweight Charts library, which introduces powerful multi-pane capabilities perfect for technical analysis. This component allows you to create professional-grade financial charts with multiple indicators stacked vertically, similar to popular trading platforms.

Key features:

- Multi-pane chart layouts for price and indicators
- Customizable themes and styles
- Technical indicators (RSI, MACD, Volume, Williams %R)
- Advanced overlay indicators (AVWAP, Pivot Points)
- Yield curve visualization
- Screenshot functionality

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install git+https://github.com/locupleto/streamlit-lightweight-charts-v5.git --force-reinstall
```

## Quick Start

```python
import streamlit as st
from lightweight_charts_v5 import lightweight_charts_v5_component

# Create a simple chart
result = lightweight_charts_v5_component(
    name="My Chart",
    charts=[{
        "chart": {"layout": {"background": {"color": "#FFFFFF"}}},
        "series": [{
            "type": "Line",
            "data": [
                { time: '2019-04-11', value: 80.01 },
                { time: '2019-04-12', value: 96.63 },
                { time: '2019-04-13', value: 76.64 },
                { time: '2019-04-14', value: 81.89 },
                { time: '2019-04-15', value: 74.43 },
                { time: '2019-04-16', value: 80.01 },
                { time: '2019-04-17', value: 96.63 },
                { time: '2019-04-18', value: 76.64 },
                { time: '2019-04-19', value: 81.89 },
                { time: '2019-04-20', value: 74.43 },
            ],
            "options": {"color": "#2962FF"}
        }],
        "height": 300
    }],
    height=300
)
```

## Demo Application

The repository includes a `demo/` directory with example scripts that showcase how to use the component. These scripts include:

- `chart_demo.py`: Stock chart visualization with multiple indicators
- `chart_themes.py`: Theme customization (Light, Dark, Black, Custom)
- `indicators.py`: Different price chart styles (Candlestick, Bar, Line) and technical indicators
- `yield_curve.py`: Yield curve visualization

## Running the Demo Application

To test the demo scripts, first install the package and required dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install git+https://github.com/locupleto/streamlit-lightweight-charts-v5.git --force-reinstall
pip install streamlit yfinance numpy
```

Then, run the example script using **Streamlit**:

```bash
streamlit run demo/chart_demo.py
```

## License

This project is licensed under the MIT License.
