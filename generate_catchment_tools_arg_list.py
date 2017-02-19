import argparse
import json
from glob import glob

parser = argparse.ArgumentParser(description='Process Hydrologic Reference Stations metadata.')
parser.add_argument('hrs_dir', metavar='HRS_DIRECTORY', type=str, help='Directory containing HRS metadata.')
parser.add_argument('--debug', action='store_true', help='Enable debug output.')

args = parser.parse_args()

cc_providers = [
    'w00067',
    'w00066',
    'w00077',
    'w00074',
    'w00231',
    'w00151',
    'w00129',
    'w00072',
    'w00002',
    'w00075',
    'w00078',
    'w00003',
    'w00209',
]

for station_file in glob(args.hrs_dir + '/*.json'):
    with open(station_file) as f:
        station_data = json.load(f)

    if station_data['data_owner_code'][0] in cc_providers:
        location = station_data['location'][0].replace("&deg;E, ", ",-").replace("&deg;S", "")
        print(location + ':' + station_data['awrc'][0])

