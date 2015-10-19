import argparse
import os
import sys
import datetime
import pandas
from sqlalchemy.exc import IntegrityError
from phildb.database import PhilDB

def main(phildb_name, hrs_data_files):
    db = PhilDB(phildb_name)

    db.add_source('BOM_HRS', 'Bureau of Meteorology; Hydrological Reference Stations dataset.')

    freq = 'D'

    hrs_header_len = 18

    for hrs_file in hrs_data_files:
        print("Processing file: ", hrs_file, '...')
        station_id = os.path.basename(hrs_file).split('_')[0]
        print("Using station ID: ", station_id, '...')
        try:
            with open(hrs_file) as datafile:
                header=[next(datafile) for x in range(hrs_header_len)]
            header = ''.join(header)
            df = pandas.read_csv(hrs_file, parse_dates=True, index_col='Date', skiprows=hrs_header_len)
            try:
                db.add_timeseries(station_id)
            except IntegrityError:
                pass
            db.add_timeseries_instance(station_id, freq, header, measurand = 'Q', source = 'BOM_HRS')
            db.write(station_id, freq, df, measurand = 'Q', source = 'BOM_HRS')
        except ValueError as e:
            print("Skipping unloadable text file: ", hrs_file)
            pass

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Load the HRS data.')

    parser.add_argument('--phildb-name', type=str,
                        default = 'hm_tsdb',
                        help='PhilDB to load the data into.')

    parser.add_argument('hrs_data_files', type=str, nargs='+',
                        help='HRS data files to load.')

    args = parser.parse_args()
    main(args.phildb_name, args.hrs_data_files)
