# Demo Files

This folder contains demo applications and supporting library modules for the `streamlit-lightweight-charts-v5` component.

## Runnable Demos

These files can be run directly with `streamlit run`:

| File | Command | Description |
|------|---------|-------------|
| `chart_demo.py` | `streamlit run demo/chart_demo.py` | Full-featured demo with multiple chart types, themes, indicators, and screenshot functionality. Includes StockChart, Yield Curve, and Multi-Chart demos via dropdown selector. |
| `minimal_demo.py` | `streamlit run demo/minimal_demo.py` | Simple example showing basic AAPL stock chart with minimal code. Good starting point for new users. |
| `test_component.py` | `streamlit run demo/test_component.py` | Component test using generated data (no API calls). Useful for verifying the component works without external dependencies. |

## Library Modules (Not Runnable)

These files are **supporting modules** imported by the runnable demos. Running them directly with `streamlit run` will show an empty screen:

| File | Purpose |
|------|---------|
| `chart_themes.py` | Defines `ChartTheme` dataclass and `ChartThemes` with predefined themes (light, dark, black, custom). |
| `indicators.py` | Defines technical indicator classes: `PriceIndicator`, `VolumeIndicator`, `SMAIndicator`, `RSIIndicator`, `MACDIndicator`, `WilliamsRIndicator`. |
| `multi_demo.py` | Contains `run_multi_chart_demo()` function for displaying multiple stock charts in a grid layout. |
| `yield_curve.py` | Contains `get_yield_curve_config()` function for yield curve chart configuration. |

## Accessing All Features

To access Yield Curve and Multi-Chart demos, run the main demo:

```bash
streamlit run demo/chart_demo.py
```

Then use the **"Select Demo"** dropdown in the top-left to choose:
- **StockChart Demo** - Candlestick/Bar/Line charts with technical indicators
- **Yield Curve Demo** - Interest rate yield curve visualization
- **Multi-Chart Demo** - Grid of multiple stock area charts

## Requirements

Install demo dependencies:

```bash
pip install streamlit-lightweight-charts-v5[demo]
```

Or manually:

```bash
pip install yfinance numpy
```
