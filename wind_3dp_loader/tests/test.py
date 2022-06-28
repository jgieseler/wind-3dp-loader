import numpy as np
import pandas as pd
from wind_3dp_loader import wind3dp_load


def test_wind3dp_load():
    df, meta = wind3dp_load(dataset="WI_SFPD_3DP",
                            startdate="2021/04/16",
                            enddate="2021/04/18",
                            resample='1min',
                            multi_index=True,
                            path=None)

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2880, 76)

    # Check that fillvals are replaced by NaN
    assert np.sum(np.isnan(df['FLUX_E0', 'FLUX_E0_P0'])) == 169
