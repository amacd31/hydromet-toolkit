import argparse
import calendar
import copy
import glob
import shutil
import subprocess

import numpy as np
import pandas as pd

from sqlalchemy.exc import IntegrityError

from datetime import date

import catchment_tools as ct
from phildb.database import PhilDB
from phildb.exceptions import DuplicateError

def main(phildb_name, grid_dir, awap_dir, measurand):
    db = PhilDB(phildb_name)

    source = 'CSIRO_AWAP_26J'
    if measurand == 'P':
        data_type = 'Precip'
    elif measurand == 'PE':
        data_type = 'FWPT'
    else:
        raise ValueError("Unknown measurand {0}".format(measurand))

    try:
        db.add_measurand('PE', 'POTENTIAL_EVAPORATION', 'Potential Evaporation')
    except DuplicateError:
        pass

    try:
        db.add_measurand('P', 'PRECIPTATION', 'Preciptation')
    except DuplicateError:
        pass

    try:
        db.add_source('CSIRO_AWAP_26J', 'CSIRO AWAP')
    except DuplicateError:
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
            except DuplicateError:
                pass
            try:
                db.add_timeseries_instance(catchment_id, 'MS', 'CSIRO AWAP Potential evaporation run 26j', source = 'CSIRO_AWAP_26J', measurand = measurand)
            except DuplicateError:
                pass
        except ValueError:
            pass

    awap_zip = awap_dir + "{data_type}/{year}0101_{year}1231.{data_type}.run26j.flt.zip"

    csiro_year_data = '/dev/shm/csiro_year_data_tmp'
    for year in range(1900, 2014):
        results = copy.deepcopy(catchment_data_template)

        zip_file = awap_zip.format(year = year, data_type = data_type)
        print(zip_file)
        p = subprocess.Popen(['unzip', '-o', '-d', csiro_year_data, zip_file])
        outdata, errdata = p.communicate()


        for month in range(1, 13):
            print((year, month))
            ndays = calendar.monthrange(year, month)
            awap_grid_file = csiro_year_data + "/AWAP/Run26j/{data_type}/mth_{data_type}_{year}{month:02d}{ndays:02d}.flt".format(year = year, month = month, ndays = ndays[1], data_type = data_type)

            # Convert from metres/day to mm/month.
            process_method = lambda x: (np.array(x) * 1000).mean() * ndays[1]

            r = ct.get_values_for_catchments(awap_grid_file, catchments, process_method)
            for catchment in r.keys():
                results[catchment]['date'].append(date(year,month,1))
                results[catchment]['value'].append(r[catchment])

        for c in results.keys():
            db.write(c, 'MS', pd.Series(results[c]['value'], results[c]['date']), source = 'CSIRO_AWAP_26J', measurand = measurand)

        shutil.rmtree(csiro_year_data)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process CSIRO AWAP data.')
    parser.add_argument('measurand', type=str,
                        help='Measurand to load. (e.g. P or PE)')

    parser.add_argument('--grid_dir', type=str,
                        default = './data/catchment_grids/',
                        help='Directory containg catchment grid CSV files.')

    parser.add_argument('--awap_dir', type=str,
                        default = './data/csiro_awap_run_26j/',
                        help='Directory containg AWAP data files.')

    parser.add_argument('--phildb-name', type=str,
                        default = 'hm_tsdb',
                        help='PhilDB to load the data into.')

    args = parser.parse_args()
    main(args.phildb_name, args.grid_dir, args.awap_dir, args.measurand)
