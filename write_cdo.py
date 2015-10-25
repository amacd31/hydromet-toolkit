import bom_data_parser as bdp
import argparse

import pandas as pd

from phildb.database import PhilDB

from hydromet.loader import load_cdo

def main():
    parser = argparse.ArgumentParser(description='Write Bureau of Meterology Climate Data Online data into a PhilDB.')
    parser.add_argument('dbname')
    parser.add_argument('files', nargs="+")

    args = parser.parse_args()
    db = PhilDB(args.dbname)

    load_cdo(db, args.files)

if __name__ == "__main__":
    main()
