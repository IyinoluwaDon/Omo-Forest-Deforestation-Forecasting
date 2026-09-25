import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import subprocess

st.set_page_config(page_title="Omo Forest NDVI Dashboard", layout="wide")

st.title("🌳 Omo Forest Reserve — NDVI Vegetation Monitor")
st.caption(
    "Sentinel-2 based NDVI time series and LSTM forecast over Omo Forest "
    "Reserve, Ogun State, Nigeria. Built entirely with free tools "
    "(Google Earth Engine, Colab, TensorFlow)."
)

# ---------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------
st.sidebar.header("Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload omo_ndvi_monthly.csv (exported from the notebook's Step 2)",
    type=["csv"],
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, parse_dates=["date"])
else:
    st.info(
        "No file uploaded — showing example/demo data. "
        "Upload your own `omo_ndvi_monthly.csv` from the notebook to see real results."
    )
    # Small demo dataset so the app isn't empty on first load
    demo_dates = pd.date_range("2023-01-01", periods=16, freq="MS")
    demo_values = [
        0.578, 0.388, 0.630, 0.694, 0.759, 0.752, 0.744, 0.737,
        0.730, 0.723, 0.708, 0.460, 0.436, 0.653, 0.728, 0.705,
    ]
    df = pd.DataFrame({"date": demo_dates, "ndvi": demo_values})
    df["image_count"] = 1

df = df.sort_values("date").reset_index(drop=True)

# ---------------------------------------------------------------
# Summary stats
# ---------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Months of data", len(df))
col2.metric("Mean NDVI", f"{df['ndvi'].mean():.3f}")
col3.metric("Min NDVI", f"{df['ndvi'].min():.3f}")
col4.metric("Max NDVI", f"{df['ndvi'].max():.3f}")

# ---------------------------------------------------------------
# Time series chart
# ---------------------------------------------------------------
st.subheader("NDVI Time Series")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df["date"], y=df["ndvi"],
    mode="lines+markers", name="NDVI",
    line=dict(color="seagreen"),
))
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="NDVI",
    height=450,
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)

st.caption(
    "NDVI ranges from -1 to 1. Values above ~0.6 typically indicate dense, "
    "healthy vegetation; values below ~0.3 indicate bare soil, degraded land, "
    "or sparse vegetation."
)

# ---------------------------------------------------------------
# Date-range explorer
# ---------------------------------------------------------------
st.subheader("Explore a Date Range")

min_date, max_date = df["date"].min(), df["date"].max()
date_range = st.slider(
    "Select range",
    min_value=min_date.to_pydatetime(),
    max_value=max_date.to_pydatetime(),
    value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
)

filtered = df[(df["date"] >= date_range[0]) & (df["date"] <= date_range[1])]

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=filtered["date"], y=filtered["ndvi"],
    marker_color=filtered["ndvi"],
    marker_colorscale="RdYlGn",
    name="NDVI",
))
fig2.update_layout(height=350, xaxis_title="Date", yaxis_title="NDVI")
st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------------
# Forecast section (optional, if forecast CSV provided)
# ---------------------------------------------------------------
st.subheader("Forecast (Optional)")
forecast_file = st.sidebar.file_uploader(
    "Upload forecast CSV (columns: date, forecast_ndvi) if available",
    type=["csv"],
    key="forecast",
)

if forecast_file is not None:
    forecast_df = pd.read_csv(forecast_file, parse_dates=["date"])

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df["date"], y=df["ndvi"],
        mode="lines+markers", name="Historical NDVI",
        line=dict(color="seagreen"),
    ))
    fig3.add_trace(go.Scatter(
        x=forecast_df["date"], y=forecast_df["forecast_ndvi"],
        mode="lines+markers", name="Forecast",
        line=dict(color="orange", dash="dash"),
    ))
    fig3.update_layout(height=450, xaxis_title="Date", yaxis_title="NDVI")
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.caption(
        "Upload a forecast CSV (from the notebook's Step 7 output) to overlay "
        "the LSTM forecast here."
    )

# ---------------------------------------------------------------
# About / methodology
# ---------------------------------------------------------------
with st.expander("About this project"):
    st.markdown("""
**Objective:** Forecast monthly vegetation health (NDVI) over Omo Forest
Reserve using Sentinel-2 satellite imagery and an LSTM neural network.

**Stack:** Google Earth Engine · Google Colab · TensorFlow/Keras ·
scikit-learn · Streamlit — $0 total cost.

**Key finding:** Cloud cover is the dominant data-quality constraint in this
tropical region; a relaxed cloud filter plus seasonal (month sin/cos)
features improved forecast accuracy meaningfully, though small-data LSTM
smoothing remains a known limitation on sharp NDVI swings.
    """)

# Dummy handler for Vercel deployment detection
def app(environ, start_response):
  status = "200 OK"
  headers = [("Content-type", "text/plain; charset=utf-8")]
  start_response(status, headers)
  return [b"Streamlit App Initialized"]
