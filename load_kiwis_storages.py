import argparse

import numpy as np
import pandas as pd

from datetime import date

from kiwis_pie import KIWIS, NoDataError
from phildb.database import PhilDB
from phildb.exceptions import DuplicateError

KIWIS_END_POINT = 'http://www.bom.gov.au/waterdata/services'
k = KIWIS(KIWIS_END_POINT)

def get_water_storage(storage_id, from_date, to_date):
    ts_list = k.get_timeseries_list(
        station_id = storage_id,
        parametertype_name = 'Storage Volume',
        ts_name = 'DMQaQc.Merged.DailyMean.24HR'
    )
    ts_id = ts_list.ts_id.values[0]
    ts = k.get_timeseries_values(ts_id = ts_id, to = to_date, **{'from': from_date})
    ts.fillna(value=np.nan, inplace=True)

    ts.index = (ts.index + pd.Timedelta(hours = 10)).normalize()

    return ts

def main(phildb_name):
    db = PhilDB(phildb_name)
    try:
        db.add_measurand('STORAGE', 'STORAGE', 'Water Storage')
    except DuplicateError:
        pass

    try:
        db.add_source('BOM_KIWIS', 'BOM_KIWIS')
    except DuplicateError:
        pass

    water_storages = k.get_station_list(
        parametertype_name = 'Storage Volume',
        return_fields=['station_name', 'station_no', 'station_id', 'custom_attributes']
    )

    for i, storage in water_storages.iterrows():
        print("Processing storage {0}".format(storage.station_no))

        try:
            db.add_timeseries(storage.station_no)
        except DuplicateError:
            pass
        try:
            db.add_timeseries_instance(storage.station_no, 'D', 'Bureau of Meteorology Water Storages', source = 'BOM_KIWIS', measurand = 'STORAGE')
        except DuplicateError:
            pass


        try:
            db.write(storage.station_no, 'D', get_water_storage(storage.station_id, date(1800,1,1), date.today()), source = 'BOM_KIWIS', measurand = 'STORAGE')
        except NoDataError:
            pass

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Load water storage data.')

    parser.add_argument('--phildb-name', type=str,
                        default = 'hm_tsdb',
                        help='PhilDB to load the data into.')

    args = parser.parse_args()
    main(args.phildb_name)
