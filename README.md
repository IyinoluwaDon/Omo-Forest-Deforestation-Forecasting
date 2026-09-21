# Vegetation Time-Series Forecasting: Omo Forest Reserve NDVI (LSTM)

## Objective
Forecast monthly vegetation health (NDVI) over Omo Forest Reserve, Ogun State,
Nigeria, using historical Sentinel-2 satellite imagery and an LSTM neural
network — entirely on free tools (Google Earth Engine, Google Colab).

## Data
- **Source:** Sentinel-2 Surface Reflectance (`COPERNICUS/S2_SR_HARMONIZED`) via Google Earth Engine
- **Area of interest:** Omo Forest Reserve bounding box (4.19–4.65°E, 6.35–7.05°N)
- **Time range:** January 2018 – May 2026
- **Processing:** Per-pixel cloud masking (QA60 band) followed by monthly
  median NDVI composites over the AOI
- **Coverage:** 74 of 108 possible months had usable imagery after cloud
  filtering (69%); the remaining months were linearly interpolated and
  explicitly flagged (`is_observed = False`) rather than silently blended in

## Method
1. Extracted monthly NDVI values via Earth Engine, using a relaxed cloud
   threshold (60%) and median compositing to recover usable observations —
   an initial stricter threshold (30%) had left only 33% real coverage
2. Built sliding-window sequences (6-month lookback) with two input
   channels in addition to NDVI: `sin`/`cos` encodings of calendar month,
   added to give the model explicit seasonal context
3. Trained a 2-layer LSTM (32 units → dropout → dense) with early stopping
   on an 80/20 chronological train/test split

## Results
| Metric | Before seasonality features | After seasonality features |
|---|---|---|
| Test MAE | 0.073 | **0.066** |
| Test RMSE | 0.092 | **0.080** |

The seasonality features produced a genuine, if incremental, improvement
(~9-14% error reduction) and noticeably faster, cleaner convergence during
training (early stopping around epoch 27 vs. running the full 100 epochs
previously).

## Limitations
- **Cloud cover** is the dominant constraint on data quality in this region;
  even after relaxing filters, ~31% of months required interpolation
- **Dataset size** (76 training sequences) limits how much volatility the
  model can learn to trust — the forecast consistently under-predicts the
  amplitude of sharp NDVI swings (both drops and recoveries), producing a
  smoothed, lagging prediction relative to actual values. This is a known
  behavior of small-data sequence models and is the most likely explanation
  for the remaining gap, rather than a fixable implementation bug
- No farm-level or forest-specific yield/ground-truth data was available
  free of cost, so this project forecasts NDVI itself rather than a
  downstream outcome like crop yield

## Stack
Google Earth Engine (data + processing), Google Colab (compute),
TensorFlow/Keras (LSTM), scikit-learn (preprocessing/metrics),
pandas/numpy/matplotlib — $0 total cost.

## Possible future work
- Extend training data as more Sentinel-2 history accumulates over time
- Correlate NDVI trends with free FAOSTAT Nigeria agricultural yield
  statistics as a coarse validation signal
- Explore anomaly detection (e.g. Isolation Forest) as a complementary,
  label-free approach to flagging sudden vegetation loss
