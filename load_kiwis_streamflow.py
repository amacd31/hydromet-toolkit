import argparse

import numpy as np
import pandas as pd

from datetime import date

from kiwis_pie import KIWIS, NoDataError
from phildb.database import PhilDB
from phildb.exceptions import DuplicateError

KIWIS_END_POINT = 'http://www.bom.gov.au/waterdata/services'
k = KIWIS(KIWIS_END_POINT)

def get_station_streamflow_data(station_id, from_date, to_date):
    ts_list = k.get_timeseries_list(
        station_no = station_id,
        parametertype_name = 'Water Course Discharge',
        ts_name = 'DMQaQc.Merged.DailyMean.09HR'
    )
    ts_id = ts_list.ts_id.values[0]
    ts = k.get_timeseries_values(ts_id = ts_id, to = to_date, **{'from': from_date})
    ts.fillna(value=np.nan, inplace=True)

    ts.index = (ts.index + pd.Timedelta(hours = 10)).normalize()

    return ts

def get_streamflow_data(phildb_name, station_list):
    db = PhilDB(phildb_name)
    try:
        db.add_measurand('Q', 'STREAMFLOW', 'Water Course Discharge')
    except DuplicateError:
        pass

    try:
        db.add_source('BOM_KIWIS', 'BOM_KIWIS')
    except DuplicateError:
        pass

    for station_id in station_list:

        try:
            sf = get_station_streamflow_data(station_id, date(1800,1,1), date.today())
        except NoDataError:
            continue

        print("Processing station {0}".format(station_id))

        try:
            db.add_timeseries(station_id)
        except DuplicateError:
            pass
        try:
            db.add_timeseries_instance(station_id, 'D', 'Bureau of Meteorology Water Data Online', source = 'BOM_KIWIS', measurand = 'Q')
        except DuplicateError:
            pass

        db.write(station_id, 'D', sf, source = 'BOM_KIWIS', measurand = 'Q')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Load streamflow station data.')

    parser.add_argument('--phildb-name', type=str,
                        default = 'hm_tsdb',
                        help='PhilDB to load the data into.')

    parser.add_argument('stations', metavar='STATION', type=str, nargs='+',
                        help='List of stations to fetch data for.')

    args = parser.parse_args()
    get_streamflow_data(args.phildb_name, args.stations)
