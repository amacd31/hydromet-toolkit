import argparse
import calendar
import copy
import glob
import subprocess

import numpy as np
import pandas as pd

from datetime import date

import catchment_tools as ct
from tsdb.database import TSDB

def main(tsdb_name, grid_dir, awap_rainfall_dir):
    db = TSDB(tsdb_name)
    try:
        db.add_measurand('P', 'PRECIPITATION', 'Rainfall')
    except:
        pass

    try:
        db.add_source('BOM_AWAP', 'BoM AWAP')
    except:
        pass

    catchment_grids = glob.glob(grid_dir + '*.csv')

    catchment_data_template = {}
    catchments = {}
    for grid_csv in catchment_grids:
        try:
            catchment_id = grid_csv.replace(grid_dir, '').replace('.csv', '')
            grid_cells = pd.read_csv(grid_csv, sep=',', header=None).values
            if len(grid_cells) <= 2:
                continue
            catchments[catchment_id] = grid_cells
            catchment_data_template[catchment_id] = {'date': [], 'value': []}
            try:
                db.add_timeseries(catchment_id)
            except:
                pass
            try:
                db.add_timeseries_instance(catchment_id, 'D', 'AWAP rainfall', source = 'BOM_AWAP', measurand = 'P')
            except:
                pass
        except ValueError:
            pass

    awap_zip = awap_rainfall_dir + "{year}/{year}{month:02d}{day:02d}{year}{month:02d}{day:02d}.grid.Z"

    awap_ascii = './tmp_awap.grid'
    for year in range(1900, 2015):
        results = copy.deepcopy(catchment_data_template)
        for month in range(1, 13):
            print((year, month))
            ndays = calendar.monthrange(year, month)
            for day in range(1, ndays[1] + 1):

                zip_file = awap_zip.format(year = year, month = month, day = day)
                with open(awap_ascii, 'w') as out_file:
                    p = subprocess.Popen(['gunzip', '-c', zip_file], stdout=out_file)
                    outdata, errdata = p.communicate()

                r = ct.get_values_for_catchments(awap_ascii, catchments, np.mean)
                for catchment in r.keys():
                    results[catchment]['date'].append(date(year,month,day))
                    results[catchment]['value'].append(r[catchment])

        for c in results.keys():
            db.write(catchment, 'D', (results[c]['date'], results[c]['value']), source = 'BOM_AWAP', measurand = 'P')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--grid_dir', type=str,
                        default = './data/catchment_grids/',
                        help='Directory containg catchment grid CSV files.')

    parser.add_argument('--awap_dir', type=str,
                        default = './data/awap_rainfall/',
                        help='Directory containg AWAP data files.')

    parser.add_argument('--tsdb_name', type=str,
                        default = 'awap_rainfall_db',
                        help='TSDB to load the data into.')

    args = parser.parse_args()
    main(args.tsdb_name, args.grid_dir, args.awap_dir)
