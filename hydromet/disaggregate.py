from calendar import monthrange
import pandas as pd

def monthly_to_daily(ts):
    df = pd.DataFrame({'ts': ts}).reset_index()
    df['ndays'] = df.date.apply(lambda x: monthrange(x.year,x.month)[1])
    df.set_index('date', inplace=True)

    return df.eval('ts / ndays').resample('D').interpolate()
