# Omo Forest NDVI Forecasting

A pipeline that pulls monthly Sentinel-2 vegetation data (NDVI) for **Omo Forest Reserve, Ogun State, Nigeria** from Google Earth Engine, then trains an LSTM to forecast next month's vegetation health. It runs entirely on free tools.

**Status:** working end to end, open to collaborators. See [Known weaknesses](#known-weaknesses) and [How to contribute](#how-to-contribute).

## Problem

Omo is one of Nigeria's last large rainforest blocks and is under logging and land-use pressure. Ground surveys of an area this size are slow and expensive. Sentinel-2 imagery is free and refreshes every few days, so the goal is to turn it into a vegetation signal that can be tracked and forecast.

**NDVI** (Normalized Difference Vegetation Index) compares near-infrared and red light:

```
NDVI = (NIR - Red) / (NIR + Red)      # Sentinel-2 bands B8 and B4
```

Dense forest scores about 0.6 to 0.9. Bare or degraded land scores below about 0.3.

## How it works

| Stage | What happens |
|---|---|
| 1. Source | Sentinel-2 collection `COPERNICUS/S2_SR_HARMONIZED` on Google Earth Engine (GEE). Processing runs server-side, so nothing large is downloaded. |
| 2. Cloud handling | Two layers. Scenes with more than 60% cloud are dropped. The rest get a per-pixel mask (QA60 bits 10 and 11). |
| 3. Compositing | One median NDVI composite per month. Median resists leftover cloud and shadow noise better than mean. |
| 4. Spatial reduction | Each composite is reduced to one median NDVI value for the whole bounding box at 100 m scale. Result: one number per month. |
| 5. Gap filling | Months with no usable imagery are linearly interpolated. Every point carries an `is_observed` flag so real and filled values are never confused. |
| 6. Features | A 6-month sliding window. Each timestep has 3 channels: scaled NDVI, `sin(2π·month/12)`, `cos(2π·month/12)`. The sin/cos pair encodes seasonality and puts December next to January. |
| 7. Model | LSTM(32) → Dropout(0.2) → Dense(16) → Dense(1). MSE loss, Adam, early stopping. Chronological 80/20 split, no shuffling. |
| 8. Forecast | One-step-ahead prediction. The 6-month forward forecast feeds its own predictions back in and computes the correct calendar month features at each step. |

### Data

| Item | Detail |
|---|---|
| Area of interest | Bounding box `[4.19, 6.35, 4.65, 7.05]` (lon/lat) |
| Period | January 2018 to May 2026 |
| Coverage | 74 of 101 months are real observations (73%). 27 are interpolated. |
| Test set | 19 months, 16 of them real observations |

## Results

| Metric | NDVI only | With seasonality features |
|---|---|---|
| Test MAE | 0.073 | **0.066** |
| Test RMSE | 0.092 | **0.080** |

Adding seasonality cut RMSE by about 14% and made training converge faster (early stopping near epoch 27 instead of running all 100 epochs).

### Problems found and fixed along the way

| Problem | Cause | Fix |
|---|---|---|
| First run had only 16 of 48 usable months | A 30% cloud threshold rejected most scenes in a tropical rainforest | Raised threshold to 60%, switched mean to median, extended history back to 2018 |
| Forecast lagged behind real swings | The model had no calendar signal and could only react to changes | Added `month_sin` and `month_cos` inputs |

## Known weaknesses

These are the honest gaps. Most of them are good places to start contributing.

1. **No baseline comparison.** ~~The LSTM has not been compared against a persistence model ("next month equals this month") or a seasonal-naive model.~~ **Fixed (notebook Step 6):** persistence (lag-1) and seasonal-naive (lag-12) baselines are now computed on real NDVI alongside the LSTM. Rolling-origin cross-validation is still open. On a noisy series with 19 test points, a simple baseline may match or beat the LSTM — check the printed comparison.
2. **Minor data leakage.** ~~The scaler is fit on the full series before the train/test split. It should be fit on the training portion only.~~ **Fixed (notebook Step 4):** the `MinMaxScaler` is now fit on the first 80% of raw months (train period) only, then applied to the full series. Note: gap-interpolation in Step 3 still uses the whole series (linear `interpolate`), which is a much smaller residual leak at gap boundaries.
3. **Under-prediction of swings.** The forecast is smoother than reality and misses sharp drops. Small data is the likely cause, but that is a hypothesis, not a proven result.
4. **Spatial information is discarded.** Averaging the whole reserve into one number hides where change happens, which is the real question for deforestation.
5. **Rough AOI.** The area is a hand-drawn rectangle, not the official reserve boundary.
6. **Slow extraction.** About 100 sequential `getInfo()` calls. This could be one batched server-side reduction.
7. **Tiny evaluation set.** ~~A single chronological split with 19 test points gives a noisy error estimate.~~ **Fixed (notebook Step 6b):** expanding-window rolling-origin CV (4 folds × 10 months = 40 test points) reports mean ± std for LSTM vs both baselines and saves `chart_rolling_cv.png`. The original single split is kept for the forecast-vs-actual chart.
8. **NDVI, not yield.** No free farm-level or forest-level ground truth was available, so the model forecasts NDVI itself, not crop yield or deforestation area.

## How to contribute

Suggested tasks, roughly in priority order:

1. **Baselines and evaluation.** ~~Add persistence and seasonal-naive models. Replace the single split with rolling-origin cross-validation.~~ **Done (Steps 6, 6b).** Remaining: move the pipeline from the notebook into a reproducible script with a config file.
2. **Fix the scaler leakage** and move the pipeline from a notebook into a reproducible script with a config file.
3. **Speed up extraction.** Use `ImageCollection.map` with `reduceRegion` or `reduceRegions` and a single export instead of per-month calls.
4. **Spatial modelling.** Per-pixel or per-grid-cell series, change detection, or a ConvLSTM, so the output shows where vegetation is declining.
5. **Better inputs.** Sentinel-1 radar sees through cloud and could cut interpolation. Rainfall data (CHIRPS) is free and likely explains much of the seasonal swing.
6. **Anomaly detection.** Flag sudden NDVI drops without labels, for example with Isolation Forest.
7. **Official boundary.** Replace the bounding box with the real reserve polygon.
8. **Productionising.** Tests, CI, and a dashboard that reads live data instead of an uploaded CSV.

If you want to pick something up, open an issue first so we do not duplicate work.

## Repository structure

```
omo-ndvi-forecast/
├── omo_ndvi_forecast.ipynb   # Full pipeline: GEE extraction, LSTM, evaluation, maps, charts
├── app.py                    # Streamlit dashboard
├── requirements.txt          # Dashboard dependencies
├── omo_ndvi_monthly.csv      # Exported NDVI series (generated by the notebook)
└── README.md
```

## Run it

### Notebook (Google Colab)

1. Register for free at [Google Earth Engine](https://code.earthengine.google.com/register) (Community tier, non-commercial) and note your Cloud Project ID.
2. Upload `omo_ndvi_forecast.ipynb` to [Google Colab](https://colab.research.google.com/).
3. In the first code cell, replace `'your-project-id'` with your project ID.
4. Run all cells top to bottom. The full 2018 to 2026 extraction makes about 100 Earth Engine calls, so it takes a while.

The notebook writes `omo_ndvi_monthly.csv`, a spatial NDVI map, and four chart PNGs (history, forecast-vs-actual, training history, rolling-CV).

### Dashboard (local)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Upload `omo_ndvi_monthly.csv` in the sidebar to see real data. Without an upload, the app shows a small demo series.

### Dashboard (deploy free)

Push `app.py` and `requirements.txt` to GitHub, deploy on [Streamlit Community Cloud](https://share.streamlit.io), and set the main file to `app.py`.

## Tech stack

Google Earth Engine, geemap, Google Colab, TensorFlow/Keras, scikit-learn, pandas, NumPy, Matplotlib, Plotly, Streamlit. Total cost: $0.

## Author

Iyinoluwa Don-Taiwo · [GitHub](https://github.com/IyinoluwaDon)
