import argparse

import pandas as pd

from phildb.create import create
from phildb.database import PhilDB
from phildb.exceptions import AlreadyExistsError

def make_db(dbname):
    try:
        create(dbname)
    except AlreadyExistsError:
        print("'{0}' already exists. Aborting.".format(dbname))
        exit(1)

    db = PhilDB(dbname)
    db.add_timeseries('APSLEY')
    db.add_source('MACDONALD', '33 Benayeo Road')
    db.add_measurand('T_OUT', 'temperature_outside', 'Outside temperature')

    db.add_measurand('T_IN', 'temperature_inside', 'Inside temperature')

    db.add_measurand('HUM_OUT', 'humidity_outside', 'Humidity outside')

    db.add_measurand('HUM_IN', 'humidity_inside', 'Humitity inside')

    db.add_measurand('ABS_PRESSURE', 'absolulte_pressure', 'Absolute air pressure')

    for m in ['T_OUT', 'T_IN', 'HUM_OUT', 'HUM_IN', 'ABS_PRESSURE']:
        db.add_timeseries_instance('APSLEY', '5T', '', source='MACDONALD', measurand = m)

def main():
    parser = argparse.ArgumentParser(description='Create database from pywws data.')
    parser.add_argument('dbname')
    parser.add_argument('--new', dest='is_new', action='store_true',
                          help='Create from scratch.')

    parser.add_argument('files', nargs='+')
    args = parser.parse_args()

    if args.is_new:
        make_db(args.dbname)

    db = PhilDB(args.dbname)

    key_map = {
        'HUM_IN': 'hum_in',
        'T_IN': 'temp_in',
        'HUM_OUT': 'hum_out',
        'T_OUT': 'temp_out',
        'ABS_PRESSURE': 'abs_pressure',
    }

    for f in args.files:
        data = pd.read_csv(f, names = ['idx', 'delay', 'hum_in', 'temp_in', 'hum_out', 'temp_out', 'abs_pressure', 'wind_ave', 'wind_gust', 'wind_dir', 'rain', 'status'], parse_dates=True, index_col='idx').resample('5T')

        for m in ['T_OUT', 'T_IN', 'HUM_OUT', 'HUM_IN', 'ABS_PRESSURE']:
            k = key_map[m]
            db.write('APSLEY', '5T', data[k], source='MACDONALD', measurand=m)

    print(data.describe())


if __name__ == "__main__":
    main()
