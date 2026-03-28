import streamlit as st
from lightweight_charts_v5 import lightweight_charts_v5_component
import numpy as np
import yfinance as yf
from chart_themes import ChartThemes
from indicators import PriceIndicator, VolumeIndicator, VolumeProfileIndicator


def main():
    st.set_page_config(layout="wide", page_title="Volume Profile Demo")

    # --- Sidebar controls ---
    st.sidebar.header("Chart Settings")
    symbol = st.sidebar.text_input("Symbol", value="AAPL")
    period = st.sidebar.selectbox("Period", ["6mo", "1y", "2y", "5y"], index=1)
    theme_name = st.sidebar.selectbox("Theme", ["Light", "Dark", "Black"], index=1)
    theme_map = {
        "Light": ChartThemes.light(),
        "Dark": ChartThemes.dark(),
        "Black": ChartThemes.black(),
    }
    theme = theme_map[theme_name]

    st.sidebar.header("Volume Profile Settings")
    num_bins = st.sidebar.slider("Price Bins", 10, 80, 40)
    left_strength = st.sidebar.slider("Pivot Left Strength", 5, 50, 20)
    right_strength = st.sidebar.slider("Pivot Right Strength", 5, 50, 20)
    profile_bar_count = st.sidebar.slider("Profile Width (bars)", 5, 40, 20)
    value_area_pct = st.sidebar.slider("Value Area %", 10, 90, 50)
    show_poc = st.sidebar.checkbox("Show POC", value=True)
    show_value_area = st.sidebar.checkbox("Show Value Area", value=True)

    # --- Fetch data ---
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        df = df.reset_index()
        df = df.rename(columns={
            'Date': 'date', 'Open': 'open', 'High': 'high',
            'Low': 'low', 'Close': 'close', 'Volume': 'volume'
        })
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        df = df.replace({np.nan: None})

        title = f"{symbol} - {ticker.info.get('shortName', 'Volume Profile')}"
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return

    # --- Calculate volume profile ---
    vp = VolumeProfileIndicator(
        df,
        left_strength=left_strength,
        right_strength=right_strength,
        num_bins=num_bins,
        profile_bar_count=profile_bar_count,
        show_poc=show_poc,
        show_value_area=show_value_area,
        value_area_percent=value_area_pct,
    )
    vp.calculate()
    vp_rectangles = vp.get_rectangles()
    vp_series = vp.get_series_configs()

    # --- Build chart panes ---
    price_indicator = PriceIndicator(
        df, height=500,
        title=title,
        style="Candlestick",
        overlays=[],
        rectangles=vp_rectangles,
        theme=theme,
    )
    price_indicator.calculate()
    price_pane = price_indicator.pane()
    price_pane["series"].extend(vp_series)

    volume_indicator = VolumeIndicator(df, height=120, theme=theme)
    volume_indicator.calculate()

    charts_config = [price_pane, volume_indicator.pane()]
    total_height = 500 + 120

    # --- Render ---
    @st.fragment
    def render_chart():
        return lightweight_charts_v5_component(
            name=symbol,
            charts=charts_config,
            height=total_height,
            zoom_level=150,
            key="volume_profile_chart",
        )

    render_chart()


if __name__ == "__main__":
    main()
