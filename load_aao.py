import argparse
import calendar
import copy
import glob
import shutil
import subprocess

import numpy as np
import pandas as pd

from sqlalchemy.exc import IntegrityError

from datetime import datetime
from urllib2 import urlopen

from tsdb.database import TSDB
from tsdb.exceptions import DuplicateError

def main(tsdb_name):
    db = TSDB(tsdb_name)
    try:
        db.add_measurand('CX', 'CLIMATE_INDEX', 'Climate Index')
    except IntegrityError:
        pass

    try:
        db.add_source('NOAA', 'NOAA')
    except IntegrityError:
        pass

    try:
        db.add_timeseries('AAO')
    except IntegrityError:
        pass
    try:
        db.add_timeseries_instance('AAO', 'MS', 'NOAA Antarctic Oscillation Index', source = 'NOAA', measurand = 'CX')
    except DuplicateError:
        pass

    dateparse = lambda x,y: datetime.strptime(x+y, '%Y%m')
    aao = pd.read_csv(urlopen('http://www.cpc.ncep.noaa.gov/products/precip/CWlink/daily_ao_index/aao/monthly.aao.index.b79.current.ascii'), header=None, parse_dates=[[0,1]], sep='\s+', engine='python', date_parser=dateparse, index_col=0, names=['year', 'month', 'aao_value'])

    db.write('AAO', 'MS', (aao.index, aao.aao_value), source = 'NOAA', measurand = 'CX')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Load AAO data.')

    parser.add_argument('--tsdb-name', type=str,
                        default = 'hm_tsdb',
                        help='TSDB to load the data into.')

    args = parser.parse_args()
    main(args.tsdb_name)
