import pandas as pd

from numpy import sqrt

def dist_free_cusum(timeseries):
    """
        Calculate a distribution free cumlative sum of a timeseries and test against Kolmogorov-Smirnov two-sample statistic.

        :param timeseries: The timeseries to test.
        :type timeseries: pandas.Series.

        :returns: dictionary
            :dist_free_cusum: Distribution free cusum pandas series.
            :idxmax: Index of the absolute max in the dist_free_cusum.
            :max: The absolute max in the dist_free_cusum.
            :significance_level: Dictionary of signifiance levels to compare against the max. Key is percentage significance as a float.

        References:
            * McGilchrist, C. A., and K. D. Woodyer. "Note on a Distribution-Free CUSUM Technique." Technometrics 17, no. 3 (August 1, 1975): 321-25. doi:10.2307/1268068.
            * Chiew, F. H. S., and T. A. McMahon. "Detection of Trend or Change in Annual Flow of Australian Rivers." International Journal of Climatology 13, no. 6 (September 1, 1993): 643-53. doi:10.1002/joc.3370130605.

    """
    # Distribution-free Cusum from section 3 of McGilchrist and Woodyer, 1975
    q = timeseries - timeseries.median()
    q[q >= 0] = 1
    q[q < 0] = -1

    v = q.cumsum()

    # Equation 20 from Chiew and McMahon, 1993
    ks = 2.0 / len(v) * v.abs().max()

    results = {
            'dist_free_cusum': v,
            'idxmax': v.abs().idxmax(),
            'max': v.abs().max(),
            'significance_level': {
                    # Kolmogorov-Smirnov critical D-values
                    # at different levels of significance.
                    0.1: 1.22 * sqrt(len(v)), # 10%
                    0.05: 1.36 * sqrt(len(v)), # 5%
                    0.01: 1.63 * sqrt(len(v)), # 1%
                    0.005: 1.73 * sqrt(len(v)) # 0.5%
                }
            }

    return results

def ols(ts):
    """
        Calculate ordinary least squares model from a pandas time series.
    """

    df = ts.reset_index()
    df.columns = [ 'index', 'values' ]
    model = pd.ols(y = df['values'], x = pd.to_datetime(df['index']).astype(int).astype(float), intercept = True)

    df['linear_regression'] = model.predict()
    df.set_index('index', inplace = True)

    return model, df
