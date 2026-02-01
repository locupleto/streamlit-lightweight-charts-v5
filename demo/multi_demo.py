import streamlit as st
import yfinance as yf
import pandas as pd
from lightweight_charts_v5 import lightweight_charts_v5_component
from indicators import PriceIndicator
from chart_demo import HANDWRITTEN_FONTS

LARGE_US_STOCKS = [
    {"symbol": "AAPL", "name": "Apple Inc."},
    {"symbol": "MSFT", "name": "Microsoft Corporation"},
    {"symbol": "AMZN", "name": "Amazon.com Inc."},
    {"symbol": "GOOGL", "name": "Alphabet Inc."},
    {"symbol": "META", "name": "Meta Platforms Inc."},
    {"symbol": "NVDA", "name": "NVIDIA Corporation"}
]

def run_multi_chart_demo(theme, selected_theme_name):
    """Run the multi-chart demo with the provided theme"""
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

    with col1:
        history_options = ["1 Month", "3 Months", "6 Months", "1 Year"]
        selected_history = st.selectbox("History Length", history_options, index=1)

    # Parse history length
    if "Month" in selected_history:
        months = int(selected_history.split()[0])
        period = f"{months}mo"
    else:
        years = int(selected_history.split()[0])
        period = f"{years}y"

    # Wrap chart grid in fragment to prevent chart component reruns
    # from triggering full page reruns
    @st.fragment
    def render_chart_grid():
        # Create rows for the grid
        for i in range(0, len(LARGE_US_STOCKS), 2):
            cols = st.columns(2)

            # First column
            with cols[0]:
                display_chart(LARGE_US_STOCKS[i], period, theme, selected_theme_name)

            # Second column (if available)
            if i + 1 < len(LARGE_US_STOCKS):
                with cols[1]:
                    display_chart(LARGE_US_STOCKS[i + 1], period, theme, selected_theme_name)

    render_chart_grid()

def display_chart(symbol_info, period, theme, selected_theme_name):
    try:
        # Download data
        ticker = yf.Ticker(symbol_info["symbol"])
        df = ticker.history(period=period)

        # Reset index to make date a column
        df = df.reset_index()

        # Rename columns to match expected format
        df = df.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })

        # Format date exactly like chart_demo
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')

        # Create title
        title = f"{symbol_info['symbol']} - {symbol_info['name']}"

        # Create indicator with Area style instead of Line
        indicator = PriceIndicator(
            df=df,
            height=250,
            title=title,
            style="Area",  # Changed from "Line" to "Area"
            theme=theme
        )

        # Calculate indicator
        indicator.calculate()

        # Get chart configuration
        chart_config = indicator.pane()

        # Render chart
        lightweight_charts_v5_component(
            name=symbol_info["symbol"],
            charts=[chart_config],
            height=chart_config["height"],
            zoom_level=250,
            take_screenshot=False,
            configure_time_scale=False,
            fonts=HANDWRITTEN_FONTS if selected_theme_name == "Custom" else None,
            key=f"chart_{symbol_info['symbol']}"
        )

    except Exception as e:
        st.error(f"Error displaying chart for {symbol_info['symbol']}: {str(e)}")