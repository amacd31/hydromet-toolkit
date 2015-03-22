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
from urllib2 import urlopen

import bom_data_parser as bdp
from tsdb.database import TSDB
from tsdb.exceptions import DuplicateError

def main(tsdb_name):
    db = TSDB(tsdb_name)
    try:
        db.add_measurand('CX', 'CLIMATE_INDEX', 'Climate Index')
    except IntegrityError:
        pass

    try:
        db.add_source('BOM', 'BOM')
    except IntegrityError:
        pass

    try:
        db.add_timeseries('SOI')
    except IntegrityError:
        pass
    try:
        db.add_timeseries_instance('SOI', 'MS', 'Bureau of Meterology Southern Oscillation Index', source = 'BOM', measurand = 'CX')
    except DuplicateError:
        pass

    soi = bdp.read_soi_html(urlopen("ftp://ftp.bom.gov.au/anon/home/ncc/www/sco/soi/soiplaintext.html"))

    db.write('SOI', 'MS', (soi.index, soi.values), source = 'BOM', measurand = 'CX')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Load SOI data.')

    parser.add_argument('--tsdb-name', type=str,
                        default = 'hm_tsdb',
                        help='TSDB to load the data into.')

    args = parser.parse_args()
    main(args.tsdb_name)
