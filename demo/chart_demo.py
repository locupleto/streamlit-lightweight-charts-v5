import streamlit as st
from pathlib import Path
from lightweight_charts_v5 import lightweight_charts_v5_component
import numpy as np
import yfinance as yf
from chart_themes import ChartThemes
from indicators import *
from yield_curve import get_yield_curve_config
import sys
import os

# Add the current directory to the path so we can import multi_demo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Default symbol for the chart
DEFAULT_SYMBOL = "^GSPC"  # S&P 500 index
TITLE = "S&P 500 Index"

# Example optional fonts from https://fonts.google.com/
HANDWRITTEN_FONTS = [
    "Delicious Handrawn",
    "Gochi Hand",
    "Just Another Hand",
    "Patrick Hand SC",
    "Dancing Script",
    "Pacifico",
    "Caveat",
    "Reenie Beanie",
    "Grape Nuts",
    "Walter Turncoat"
]

def main():
    # Set up Streamlit page
    st.set_page_config(layout="wide")

    # Styling options + screenShot-button
    col0, col1, col2, col3, col4 = st.columns([1, 1, 1, 1, 1])

    with col0:
        demo_type = st.selectbox(
            "Select Demo",
            options=["StockChart Demo", "Yield Curve Demo", "Multi-Chart Demo"],
            index=0
        )

    with col1:
        theme_options = {
            "Light": ChartThemes.light(),
            "Dark": ChartThemes.dark(),
            "Black": ChartThemes.black(),
            "Custom": ChartThemes.custom(),
        }
        selected_theme = st.selectbox(
            "Select Theme", 
            options=list(theme_options.keys()),
            key="theme_selector"
        )
        theme = theme_options[selected_theme]

    with col2:
        # Add symbol input for yfinance
        if demo_type == "StockChart Demo":
            symbol = st.text_input("Symbol", value=DEFAULT_SYMBOL)

    with col3:
        if demo_type == "StockChart Demo":
            chart_style = st.selectbox(
                "Select Price Chart Style",
                options=["Candlestick", "Bar", "Line"],
                index=0,
                key="chart_style_selector"
            )

    # Only show screenshot button for non-multi-chart demos
    with col4:
        if demo_type != "Multi-Chart Demo":
            st.write('')
            st.write('')
            take_screenshot = st.button("Save Screenshot", key="screenshot_button")
        else:
            take_screenshot = False

    if demo_type == "StockChart Demo":
        # Fetch data using yfinance
        try:
            # Get data for the past 1000 trading days (approximately 4 years)
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1000d")

            # Reset index to make date a column
            df = df.reset_index()

            # Rename columns to match the expected format
            df = df.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })

            # Make sure date is in the right format for the chart
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')

            # Update title with the current symbol
            title = f"{symbol} - {ticker.info.get('shortName', 'Stock Chart')}"

            # Replace NaN values with None for JSON serialization
            df = df.replace({np.nan: None})

            # Create all overlay indicators to later add to the main PriceIndicator
            sma_20 = SMAIndicator(df, period=20, color="rgba(255, 140, 0, 0.8)")  # Orange
            sma_200 = SMAIndicator(df, period=200, color="rgba(25, 118, 210, 0.8)") # Blue

            # Create markers for significant points, e.g. Buy/Sell from a strategy
            buy_index = -30
            sell_index = -15

            markers = [
                {
                    "time": df['date'].iloc[buy_index], # Buy 30 days from the end
                    "position": "belowBar",  
                    "color": "#32CD32",
                    "shape": "arrowUp",
                    "text": "Buy",
                    "size": 2
                },
                {
                    "time": df['date'].iloc[sell_index], # Sell 15 days from the end
                    "position": "aboveBar", 
                    "color": "#f44336",
                    "shape": "arrowDown",
                    "text": "Sell",
                    "size": 2
                },
            ]

            # Create rectangles to highlight specific regions
            start_offset = -150
            end_offset = -100
            rectangles = [
                {
                    # Rectangle highlighting the range between 200 and 150 bars back
                    "startTime": df['date'].iloc[start_offset],
                    "startPrice": df['low'].iloc[start_offset:end_offset].min(),  # Lowest low in the range
                    "endTime": df['date'].iloc[end_offset],
                    "endPrice": df['high'].iloc[start_offset:end_offset].max(),  # Highest high in the range
                    "fillColor": "rgba(255, 255, 0, 0.5)",  # Yellow with 50% opacity
                    "borderColor": "rgba(255, 255, 0, 0.0)",  # Same color as fill
                    "borderWidth": 0,  # No border
                    "opacity": 0.5,
                    "zOrder": "bottom"  # Place it behind other elements
                }
            ]

            # Then modify the PriceIndicator creation to include the rectangles
            indicators = [
                PriceIndicator(df, height=500, 
                            title=title,
                            style=chart_style, 
                            overlays=[sma_20, sma_200], 
                            markers=markers,
                            rectangles=rectangles,  # Add the rectangles here
                            theme=theme),
                VolumeIndicator(df, height=120, theme=theme),
                RSIIndicator(df, height=120, theme=theme),
                MACDIndicator(df, height=120, theme=theme),
                WilliamsRIndicator(df, height=120, theme=theme),
            ]

            # Calculate indicators
            for indicator in indicators:
                indicator.calculate()

            # Create pane configurations
            charts_config = [indicator.pane() for indicator in indicators]

            # Calculate total height
            total_height = sum(indicator.height for indicator in indicators)

            # Wrap chart in fragment to prevent component reruns from triggering page reruns
            @st.fragment
            def render_stock_chart():
                return lightweight_charts_v5_component(
                    name=symbol,
                    charts=charts_config,
                    height=total_height,
                    zoom_level=150,
                    take_screenshot=take_screenshot,
                    fonts=HANDWRITTEN_FONTS if selected_theme == "Custom" else None,
                    key=f"chart_{demo_type}"
                )

            result = render_stock_chart()

            # Handle screenshot data if such is returned from the component
            if take_screenshot:
                handle_screenshot(result)

        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {str(e)}")
            return

    elif demo_type == "Yield Curve Demo":
        # Get yield curve configuration
        charts_config = [get_yield_curve_config(theme.to_dict())]
        total_height = 400
        symbol = "Yield Curve"

        # Wrap chart in fragment to prevent component reruns from triggering page reruns
        @st.fragment
        def render_yield_curve():
            return lightweight_charts_v5_component(
                name=symbol,
                charts=charts_config,
                height=total_height,
                zoom_level=200,
                take_screenshot=take_screenshot,
                fonts=HANDWRITTEN_FONTS if selected_theme == "Custom" else None,
                key=f"chart_{demo_type}"
            )

        result = render_yield_curve()

        # Handle screenshot data if such is returned from the component
        if take_screenshot:
            handle_screenshot(result)

    elif demo_type == "Multi-Chart Demo":
        # Import and run the multi_demo module's function with the current theme
        import multi_demo
        multi_demo.run_multi_chart_demo(theme, selected_theme)  # selected_theme is the name string

def handle_screenshot(result):
    """Handle screenshot data returned from the component"""
    if result is None:
        st.info("Waiting for screenshot data...")
    elif isinstance(result, dict):
        if result.get('type') == 'screenshot' and 'data' in result:
            import base64
            from io import BytesIO
            from PIL import Image
            import os
            from pathlib import Path
            from datetime import datetime

            try:
                # Get the base64 string from the data URL
                img_data = result['data'].split(',')[1]
                # Convert to bytes
                img_bytes = base64.b64decode(img_data)
                # Create image from bytes
                img = Image.open(BytesIO(img_bytes))

                # Create a platform-independent path
                home_dir = str(Path.home())
                desktop_dir = os.path.join(home_dir, "Desktop")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"chart_screenshot_{timestamp}.png"

                # Use desktop if it exists, otherwise use home directory
                if os.path.exists(desktop_dir):
                    save_path = os.path.join(desktop_dir, filename)
                else:
                    save_path = os.path.join(home_dir, filename)

                # Save to the determined path
                img.save(save_path)
                st.success(f"Screenshot saved to: {save_path}")
            except Exception as e:
                st.error(f"Error saving screenshot: {str(e)}")
        else:
            st.warning("Invalid screenshot data format")
    else:
        st.warning(f"Unexpected result type: {type(result)}")
        if hasattr(result, '__dict__'):
            st.write("Debug - Result attributes:", result.__dict__)

if __name__ == "__main__":
    main()