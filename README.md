# Omo Forest NDVI explorer

A Streamlit dashboard for monthly NDVI CSVs and optional forecast CSVs. The included 16-row demonstration is illustrative data, not a live satellite feed or a deforestation alert. The research notebook explores Earth Engine exports and LSTM forecasts separately; no trained model runs in this app.

```sh
python -m pip install -r requirements.txt
streamlit run app.py
python -m pip install pytest
python -m pytest -q
```

Historical CSV columns: `date,ndvi`; optional `image_count`. Forecast CSV columns: `date,forecast_ndvi`. Each month must appear once, every value must be finite and within [-1,1], and forecast months must follow history. Invalid rows produce an error rather than disappearing silently. Missing months are not imputed; chart lines can span gaps.

NDVI changes can reflect seasonality, clouds, sensor coverage, or land-cover change. Regional averages do not locate deforestation or establish its cause. Compare forecasts against seasonal and persistence baselines using a chronological holdout before making performance claims. Earth Engine access and exports require a separate authenticated account. No license for redistribution is inferred from the notebook.
