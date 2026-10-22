import pandas as pd
import pytest
from validation import monthly_series

@pytest.mark.parametrize("values",[[0.4,float("inf")],[0.4,1.1],[0.4,None]])
def test_bad_values(values):
    with pytest.raises(ValueError):monthly_series(pd.DataFrame({"date":["2024-01-01","2024-02-01"],"ndvi":values}))
def test_duplicate_and_forecast():
    frame=pd.DataFrame({"date":["2024-01-01","2024-01-20"],"ndvi":[.3,.4]})
    with pytest.raises(ValueError):monthly_series(frame)
    frame=frame.iloc[:1].rename(columns={"ndvi":"forecast_ndvi"})
    with pytest.raises(ValueError):monthly_series(frame,"forecast_ndvi",after="2024-01-31")
def test_valid_sorted():
    result=monthly_series(pd.DataFrame({"date":["2024-02-01","2024-01-01"],"ndvi":[.3,.4]}))
    assert result.ndvi.tolist()==[.4,.3]
