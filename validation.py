import numpy as np
import pandas as pd

def monthly_series(frame, value="ndvi", after=None):
    if not {"date", value}.issubset(frame.columns):
        raise ValueError(f"CSV requires date and {value} columns")
    result = frame.copy()
    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    result[value] = pd.to_numeric(result[value], errors="coerce")
    if result.empty or result["date"].isna().any() or not np.isfinite(result[value]).all():
        raise ValueError("Every row must contain a valid date and finite NDVI")
    if not result[value].between(-1, 1).all():
        raise ValueError("NDVI must be between -1 and 1")
    if result["date"].dt.to_period("M").duplicated().any():
        raise ValueError("Use exactly one observation per month")
    if after is not None and (result["date"].dt.to_period("M") <= pd.Timestamp(after).to_period("M")).any():
        raise ValueError("Forecast months must follow the historical series")
    return result.sort_values("date").reset_index(drop=True)
