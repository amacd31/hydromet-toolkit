import argparse
import calendar
import copy
import glob
import subprocess

import numpy as np
import pandas as pd

from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.exc import IntegrityError

from datetime import date

import catchment_tools as ct
from phildb.database import PhilDB
from phildb.exceptions import DuplicateError

def main(phildb_name, grid_dir, awap_rainfall_dir, start_date, end_date):
    db = PhilDB(phildb_name)

    catchment_grids = glob.glob(grid_dir + '*.csv')
    rainfall_ids = db.ts_list(source = 'BOM_AWAP', measurand = 'P')
    catchment_data_template = {}
    catchments = {}
    for grid_csv in catchment_grids:
        catchment_id = grid_csv.replace(grid_dir, '').replace('.csv', '')
        try:
            grid_cells = pd.read_csv(grid_csv, sep=',', header=None).values
        except:
            continue
        if len(grid_cells) <= 2:
            continue
        catchments[catchment_id] = grid_cells
        catchment_data_template[catchment_id] = {'date': [], 'value': []}
        if catchment_id not in rainfall_ids:
            raise Exception("Catchment not previously loaded.")

    awap_zip = awap_rainfall_dir + "{year}/{year}{month:02d}{day:02d}{year}{month:02d}{day:02d}.grid.Z"

    awap_ascii = './tmp_awap.grid'
    curr_date = start_date
    while curr_date <= end_date:
        results = copy.deepcopy(catchment_data_template)
        year = curr_date.year
        month = curr_date.month
        day = curr_date.day

        print((year, month, day))

        zip_file = awap_zip.format(year = year, month = month, day = day)
        with open(awap_ascii, 'w') as out_file:
            p = subprocess.Popen(['gunzip', '-c', zip_file], stdout=out_file)
            outdata, errdata = p.communicate()

        r = ct.get_values_for_catchments(awap_ascii, catchments, np.mean)
        for catchment in r.keys():
            results[catchment]['date'].append(date(year,month,day))
            results[catchment]['value'].append(r[catchment])

        for c in results.keys():
            db.write(c, 'D', (results[c]['date'], results[c]['value']), source = 'BOM_AWAP', measurand = 'P')

        curr_date = curr_date + relativedelta(days=1)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--grid_dir', type=str,
                        default = './data/catchment_grids/',
                        help='Directory containg catchment grid CSV files.')

    parser.add_argument('--awap_dir', type=str,
                        default = './data/awap_rainfall/',
                        help='Directory containg AWAP data files.')

    parser.add_argument('--phildb-name', type=str,
                        default = 'hm_tsdb',
                        help='PhilDB to load the data into.')

    parser.add_argument('start_date', type=str,
                        help='Start date of period to load data for.')

    parser.add_argument('end_date', type=str,
                        help='End date of period to load data for.')

    args = parser.parse_args()

    start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    end_date = datetime.strptime(args.end_date, '%Y-%m-%d')

    main(args.phildb_name, args.grid_dir, args.awap_dir, start_date, end_date)
