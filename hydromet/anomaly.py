def get_monthly_anomaly(ts, start, end):
    """
        Get monthly anomaly.

        Monthly anomalies calculated from the mean of the data between the specified start and end dates.

        :param ts: Pandas timeseries, will be converted to monthly.
        :type ts: pandas.TimeSeries
        :param start: Start date to calculated mean from.
        :type start: datetime.datetime
        :param end: End date to calculated mean from.
        :type end: datetime.datetime

        :returns: pandas.TimeSeries -- Monthly anomalies.
    """
    monthly = ts.asfreq('M')
    base = monthly.ix[start:end]
    mean = base.groupby(base.index.month).mean()

    for month in range(1,13):
        monthly.ix[monthly.index.month == month] -= mean.ix[mean.index == month].values[0]

    return monthly

def get_annual_anomaly(ts, start, end):
    """
        Get annual anomaly.

        Annual anomalies calculated from the mean of the data between the specified start and end dates.

        :param ts: Pandas timeseries, will be converted to annual.
        :type ts: pandas.TimeSeries
        :param start: Start date to calculated mean from.
        :type start: datetime.datetime
        :param end: End date to calculated mean from.
        :type end: datetime.datetime

        :returns: pandas.TimeSeries -- Annual anomalies.
    """
    annual = ts.asfreq('A')
    base = annual.ix[start:end]
    mean = base.groupby(base.index.year).mean().mean()

    annual -= mean

    return annual
