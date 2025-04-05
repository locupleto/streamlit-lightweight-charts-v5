import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from lightweight_charts_v5 import lightweight_charts_v5_component
from chart_themes import ChartThemes

# Define the largest US stock symbols
LARGE_US_STOCKS = [
    {"symbol": "AAPL", "name": "Apple Inc."},
    {"symbol": "MSFT", "name": "Microsoft Corporation"},
    {"symbol": "AMZN", "name": "Amazon.com Inc."},
    {"symbol": "GOOGL", "name": "Alphabet Inc."},
    {"symbol": "META", "name": "Meta Platforms Inc."},
    {"symbol": "NVDA", "name": "NVIDIA Corporation"}
]

# Import the same handwritten fonts used in chart_demo.py
from chart_demo import HANDWRITTEN_FONTS

def run_multi_chart_demo(theme, selected_theme_name):
    """Run the multi-chart demo with the provided theme"""
    # Create UI layout - no title or screenshot button
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

    with col1:
        history_options = ["1 Month", "3 Months", "6 Months", "1 Year"]
        selected_history = st.selectbox("History Length", history_options, index=1)

    # Parse history length
    if "Month" in selected_history:
        months = int(selected_history.split()[0])
        period = f"{months}mo"
    elif "Year" in selected_history:
        years = int(selected_history.split()[0])
        period = f"{years}y"
    else:
        period = "3mo"  # Default

    # Add CSS for smoother transitions and reduced flickering
    st.html("""
    <style>
        /* Animation for chart container */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        /* Target the chart container */
        div[data-testid="stHorizontalBlock"] div.element-container:has(iframe) {
            animation: fadeIn 1.5s ease-in-out;
            transition: all 1.5s ease-in-out;
        }

        /* Apply animation to the iframe directly */
        iframe {
            animation: fadeIn 1.5s ease-in-out;
            transition: background-color 1.5s ease-in-out;
        }

        /* Reduce flickering by stabilizing container heights */
        div.element-container:has(iframe) {
            min-height: 250px;
        }
    </style>
    """)

    # Create rows for the grid
    for i in range(0, len(LARGE_US_STOCKS), 2):
        cols = st.columns(2)

        # First column
        with cols[0]:
            symbol_info = LARGE_US_STOCKS[i]
            display_chart(symbol_info, period, theme, selected_theme_name)

        # Second column (if available)
        if i + 1 < len(LARGE_US_STOCKS):
            with cols[1]:
                symbol_info = LARGE_US_STOCKS[i + 1]
                display_chart(symbol_info, period, theme, selected_theme_name)

        # Add a small divider between rows
        st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 1px solid rgba(107, 114, 128, 0.3);'>", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def fetch_stock_data(symbol, period):
    """Fetch stock data with caching to reduce API calls and flickering"""
    try:
        data = yf.download(symbol, period=period, interval="1d", auto_adjust=True)
        if data.empty:
            return None
        return data
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

def display_chart(symbol_info, period, theme, selected_theme_name):
    """Display a single chart for a stock symbol"""
    try:
        # Download data with caching
        ticker_data = fetch_stock_data(symbol_info["symbol"], period)

        if ticker_data is None or ticker_data.empty:
            st.warning(f"No data available for {symbol_info['symbol']}")
            return

        # Calculate performance - Use .iloc[0].item() to avoid warnings
        first_close = ticker_data['Close'].iloc[0].item()
        last_close = ticker_data['Close'].iloc[-1].item()
        performance = ((last_close / first_close) - 1) * 100

        # Determine if bullish or bearish
        is_bullish = performance >= 0

        # Get colors based on theme and performance
        is_dark_theme = "Dark" in selected_theme_name or "Black" in selected_theme_name

        if is_bullish:
            if is_dark_theme:
                line_color = "rgba(76, 175, 80, 1)"  # Green
                top_color = "rgba(76, 175, 80, 0.4)"
                bottom_color = "rgba(76, 175, 80, 0.1)"
            else:
                line_color = "rgba(0, 128, 0, 1)"  # Darker Green
                top_color = "rgba(0, 128, 0, 0.4)"
                bottom_color = "rgba(0, 128, 0, 0.1)"
        else:
            if is_dark_theme:
                line_color = "rgba(255, 82, 82, 1)"  # Red
                top_color = "rgba(255, 82, 82, 0.4)"
                bottom_color = "rgba(255, 82, 82, 0.1)"
            else:
                line_color = "rgba(178, 34, 34, 1)"  # Darker Red
                top_color = "rgba(178, 34, 34, 0.4)"
                bottom_color = "rgba(178, 34, 34, 0.1)"

        # Create area chart data - Use .item() to get scalar value
        area_data = []
        for date, row in ticker_data.iterrows():
            area_data.append({
                "time": date.strftime('%Y-%m-%d'),
                "value": row['Close'].item()  # Use .item() to get scalar value
            })

        # Extract title font settings from theme
        theme_dict = theme.to_dict()
        title_font_family = theme_dict.get("titleOptions", {}).get("fontFamily", "inherit")
        title_font_size = theme_dict.get("titleOptions", {}).get("fontSize", 14)
        title_font_style = theme_dict.get("titleOptions", {}).get("fontStyle", "normal")

        # Create chart configuration
        chart_config = {
            "chart": {
                "layout": theme.to_dict()["layout"],
                "timeScale": {
                    "borderVisible": False,
                    "timeVisible": True,
                    "secondsVisible": False,
                    "rightOffset": 2,
                    "barSpacing": 6,
                    "minBarSpacing": 3,
                    "fixLeftEdge": True,
                    "fixRightEdge": True
                },
                "fontFamily": "inherit"
                # Remove title font settings from chart object
            },
            "series": [{
                "type": "Area",
                "data": area_data,
                "options": {
                    "lineColor": line_color,
                    "topColor": top_color,
                    "bottomColor": bottom_color,
                    "lineWidth": 2,
                    "priceFormat": {
                        "type": 'price',
                        "precision": 2,
                        "minMove": 0.01,
                    },
                    "priceLineVisible": False,
                }
            }],
            "height": 250,
            # Put title and title font settings at the ROOT level
            "title": f"{symbol_info['symbol']} - {symbol_info['name']} ({'+' if performance >= 0 else ''}{performance:.2f}%)",
            "titleFontFamily": title_font_family,
            "titleFontSize": title_font_size,
            "titleFontStyle": title_font_style
        }
        # Render the chart - Pass HANDWRITTEN_FONTS when using Custom theme
        lightweight_charts_v5_component(
            name=symbol_info["symbol"],
            charts=[chart_config],
            height=chart_config["height"],
            zoom_level=50,  # Smaller zoom level for better initial view
            take_screenshot=False,
            configure_time_scale=False,
            fonts=HANDWRITTEN_FONTS if selected_theme_name == "Custom" else None,
            key=f"chart_{symbol_info['symbol']}"
        )

    except Exception as e:
        st.error(f"Error displaying chart for {symbol_info['symbol']}: {str(e)}")