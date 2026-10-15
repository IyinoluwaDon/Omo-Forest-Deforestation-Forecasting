import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Omo Forest NDVI Dashboard", layout="wide")

st.title("🌳 Omo Forest Reserve — NDVI Vegetation Monitor")
st.caption(
    "Sentinel-2 based NDVI time series and LSTM forecast over Omo Forest "
    "Reserve, Ogun State, Nigeria."
    
)
st.markdown(
    """
    <iframe src="https://ghbtns.com/github-btn.html?user=IyinoluwaDon&repo=Omo-Forest-Deforestation-Forecasting&type=star&count=true&size=large" 
    frameborder="0" scrolling="0" width="170" height="30" title="GitHub"></iframe>
    """,
    unsafe_allow_html=True
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
    try:
        df = pd.read_csv(uploaded_file, parse_dates=["date"])
    except Exception as e:
        st.error(f"Could not read uploaded CSV: {e}")
        st.stop()
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

# Validate required columns and coerce types
REQUIRED_COLS = {"date", "ndvi"}
if not REQUIRED_COLS.issubset(df.columns):
    st.error(
        f"Uploaded CSV must contain columns {sorted(REQUIRED_COLS)}. "
        f"Found columns: {list(df.columns)}"
    )
    st.stop()

try:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["ndvi"] = pd.to_numeric(df["ndvi"], errors="coerce")
except Exception as e:
    st.error(f"Could not parse 'date'/'ndvi' columns: {e}")
    st.stop()

df = df.dropna(subset=["date", "ndvi"])
if df.empty:
    st.error("No valid rows found after parsing 'date' and 'ndvi'.")
    st.stop()

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

if min_date == max_date:
    st.info("Only a single month of data available — showing that point.")
    filtered = df
else:
    date_range = st.slider(
        "Select range",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
    )

    filtered = df[
        (df["date"] >= pd.to_datetime(date_range[0]))
        & (df["date"] <= pd.to_datetime(date_range[1]))
    ]

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
    try:
        forecast_df = pd.read_csv(forecast_file, parse_dates=["date"])
    except Exception as e:
        st.error(f"Could not read forecast CSV: {e}")
        st.stop()

    if not {"date", "forecast_ndvi"}.issubset(forecast_df.columns):
        st.error(
            "Forecast CSV must contain columns ['date', 'forecast_ndvi']. "
            f"Found columns: {list(forecast_df.columns)}"
        )
        st.stop()

    try:
        forecast_df["date"] = pd.to_datetime(forecast_df["date"], errors="coerce")
        forecast_df["forecast_ndvi"] = pd.to_numeric(
            forecast_df["forecast_ndvi"], errors="coerce"
        )
    except Exception as e:
        st.error(f"Could not parse forecast columns: {e}")
        st.stop()

    forecast_df = forecast_df.dropna(subset=["date", "forecast_ndvi"]).sort_values(
        "date"
    )
    if forecast_df.empty:
        st.error("No valid rows in forecast CSV after parsing.")
        st.stop()

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
