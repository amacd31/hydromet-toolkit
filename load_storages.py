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
from httplib import BadStatusLine
from time import sleep

import bom_data_parser as bdp
from phildb.database import PhilDB
from phildb.exceptions import DuplicateError

SLAKE_END_POINT = 'http://water.bom.gov.au/waterstorage/resources/data/'
SLAKE_XMLCHART_END_POINT = 'http://water.bom.gov.au/waterstorage/resources/xmlchart/'

def main(phildb_name):
    db = PhilDB(phildb_name)
    try:
        db.add_measurand('STORAGE', 'STORAGE', 'Water Storage')
    except DuplicateError:
        pass

    try:
        db.add_source('BOM', 'BOM')
    except DuplicateError:
        pass

    states = bdp.read_water_storage_states(urlopen('{0}urn:bom.gov.au:awris:common:codelist:region.country:australia'.format(SLAKE_END_POINT)))

    for state in states:
        print("Processing state/territory: {0}".format(state))
        storages = bdp.read_water_storage_urns(urlopen('{0}{1}'.format(SLAKE_END_POINT, state)))

        for storage in storages:
            print("Processing storage {0}".format(storage))

            try:
                db.add_timeseries(storage)
            except DuplicateError:
                pass
            try:
                db.add_timeseries_instance(storage, 'D', 'Bureau of Meteorology Water Storages', source = 'BOM', measurand = 'STORAGE')
            except DuplicateError:
                pass

            url = "{0}{1}".format(SLAKE_XMLCHART_END_POINT, storage)
            try:
                storage_data = bdp.read_water_storage_series(urlopen(url))
            except BadStatusLine:
                print("Encounted bad status line, sleeping for 1 second before trying again...")
                sleep(1)
                storage_data = bdp.read_water_storage_series(urlopen(url))

            db.write(storage, 'D', storage_data, source = 'BOM', measurand = 'STORAGE')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Load water storage data.')

    parser.add_argument('--phildb-name', type=str,
                        default = 'hm_tsdb',
                        help='PhilDB to load the data into.')

    args = parser.parse_args()
    main(args.phildb_name)
