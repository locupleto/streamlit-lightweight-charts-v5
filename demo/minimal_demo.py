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
st.title(f"{ticker} Stock Price Chart")

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