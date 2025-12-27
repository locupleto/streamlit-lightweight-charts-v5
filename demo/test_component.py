import streamlit as st
from lightweight_charts_v5 import lightweight_charts_v5_component
from datetime import datetime, timedelta

# Generate simple test data (no yfinance needed)
start_date = datetime(2024, 1, 1)
chart_data = []
base_price = 100.0

for i in range(100):
    date = start_date + timedelta(days=i)
    # Simple sine wave pattern
    import math
    price = base_price + 10 * math.sin(i / 10)
    chart_data.append({
        "time": date.strftime("%Y-%m-%d"),
        "value": round(price, 2)
    })

# Streamlit app
st.title("Component Test (No API calls)")

# Render the chart
lightweight_charts_v5_component(
    name="Test Chart",
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

st.success("✅ If you see a blue sine wave above, the component works!")
