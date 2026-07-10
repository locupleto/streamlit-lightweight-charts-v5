import numpy as np
import streamlit as st
import yfinance as yf
from chart_themes import ChartThemes
from indicators import IchimokuIndicator, PriceIndicator, VolumeIndicator

from lightweight_charts_v5 import lightweight_charts_v5_component


def main():
    st.set_page_config(layout="wide", page_title="Ichimoku Cloud Demo")

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

    st.sidebar.header("Ichimoku Settings")
    tenkan_period = st.sidebar.slider("Tenkan Period", 5, 20, 9)
    kijun_period = st.sidebar.slider("Kijun Period", 10, 60, 26)
    senkou_b_period = st.sidebar.slider("Senkou B Period", 20, 120, 52)
    displacement = st.sidebar.slider("Displacement", 10, 52, 26)
    show_chikou = st.sidebar.checkbox("Show Chikou Span", value=True)

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

        title = f"{symbol} - Ichimoku({tenkan_period},{kijun_period},{senkou_b_period})"
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return

    # --- Calculate Ichimoku overlay ---
    ichimoku = IchimokuIndicator(
        df,
        tenkan_period=tenkan_period,
        kijun_period=kijun_period,
        senkou_b_period=senkou_b_period,
        displacement=displacement,
        show_chikou=show_chikou,
    )

    # --- Build chart panes ---
    price_indicator = PriceIndicator(
        df, height=520,
        title=title,
        style="Candlestick",
        overlays=[ichimoku],
        theme=theme,
    )
    price_indicator.calculate()
    price_pane = price_indicator.pane()

    volume_indicator = VolumeIndicator(df, height=120, theme=theme)
    volume_indicator.calculate()

    charts_config = [price_pane, volume_indicator.pane()]
    total_height = 520 + 120

    # --- Render ---
    @st.fragment
    def render_chart():
        return lightweight_charts_v5_component(
            name=symbol,
            charts=charts_config,
            height=total_height,
            zoom_level=180,
            key="ichimoku_chart",
        )

    render_chart()


if __name__ == "__main__":
    main()
