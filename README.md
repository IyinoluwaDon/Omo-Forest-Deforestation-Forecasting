# Omo Forest NDVI Explorer

A Streamlit dashboard for inspecting monthly NDVI history and an optional future forecast series. The bundled demonstration values are illustrative rather than an observation feed or trained forecast.

## What is included

- Validation of date, finite NDVI range and duplicate months
- Historical series with future-only forecast overlay
- Clear separation between sample data and real observations

## Run locally

```sh
python -m pip install -r requirements.txt
streamlit run app.py
```

## Verify

python -m pip install pytest
python -m pytest -q

## Repository map

`app.py` contains the dashboard. `validation.py` checks uploaded/supplied series. `tests/` covers validation; `omo_ndvi_forecast.ipynb` contains the research notebook.

## Evidence and limitations

The five validation tests pass and the dashboard renders with its demonstration CSV data.

The demo does not train or execute a forecasting model. NDVI changes can reflect seasonality, clouds, sensor coverage or land-cover change and do not by themselves establish deforestation. Replace sample values with licensed, traceable observations and validate against suitable baselines before making claims.

## License

No repository license file is included. Unless the project owner adds a license, do not assume the code, data or model artifacts may be redistributed or reused. Verify third-party data and model terms separately.
