import argparse
import calendar
from datetime import date
import pandas as pd

from phildb.database import PhilDB
from phildb.exceptions import DuplicateError

def gen_row_spec(num):
    row_names = []
    row_spec = []
    row_len = 8
    for i in range(num):
        row_names += 'value{0},mflag{0},qflag{0},sflag{0}'.format(i + 1).split(',')
        row_spec += [
            (i*row_len + 21, i*row_len + 26),
            (i*row_len + 26, i*row_len + 27),
            (i*row_len + 27, i*row_len + 28),
            (i*row_len + 28, i*row_len + 29),
        ]
    return row_names, row_spec

def read_ghcnd(filename):
    col_names = ['ID', 'year', 'month', 'element']
    start_colspec = [(0,11), (11,15), (15,17), (17,21)]
    row_names, row_spec = gen_row_spec(31)
    colspec = start_colspec + row_spec

    data = pd.read_fwf(filename, colspec, header=None, names=col_names + row_names, na_values=[-9999])

    ids = data['ID'].unique()
    if len(ids) != 1:
        raise ValueError("{0} contained more than one ID.".format(filename))

    collected_data = {}
    for element in data['element'].unique():
        element_data = data.ix[data['element'] == element]

        years = element_data['year']
        months = element_data['month']
        dates = []
        values = []
        for day in range(1, 32):
            for year, month, value in zip(years, months, element_data['value{0}'.format(day)].values):
                try:
                    dates.append(date(year, month, day))
                    values.append(value)
                except ValueError:
                    # Day not in current month
                    continue

        collected_data[element] = pd.Series(values, dates)

    return ids[0], pd.DataFrame(collected_data)

def main(phildb_name, files_to_process):
    db = PhilDB(phildb_name)

    try:
        db.add_source('NOAA_GHCN', 'NOAA Global Historical Climatology Network')
    except DuplicateError:
        pass

    for filename in files_to_process:
        station_id, df = read_ghcnd(filename)

        try:
            db.add_timeseries(station_id)
        except DuplicateError:
            pass

        for col in df.columns:
            try:
                db.add_measurand(col, col, col)
            except DuplicateError:
                pass

            try:
                db.add_timeseries_instance(station_id, 'D', '', source='NOAA_GHCN', measurand=col)
            except DuplicateError:
                pass

            db.write(station_id, 'D', df[col], source='NOAA_GHCN', measurand=col)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Load ghcn-daily data.')

    parser.add_argument('--phildb-name', type=str,
                        default = 'hm_tsdb',
                        help='PhilDB to load the data into.')

    parser.add_argument('files_to_process', type=str, nargs='+',
                        default = 'hm_tsdb',
                        help='PhilDB to load the data into.')

    args = parser.parse_args()
    main(args.phildb_name, args.files_to_process)
