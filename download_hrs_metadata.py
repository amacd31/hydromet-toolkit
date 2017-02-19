import argparse
import json
import os
import requests

import logging
logger = logging.getLogger(__name__)

HRS_URL = 'http://www.bom.gov.au/water/hrs'

if __name__ == '__main__':
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description='Download the metadata JSON files for the Hydrologic Reference Stations from the Bureau of Meterology website.')
    parser.add_argument('out_dir', metavar='OUTPUT_DIRECTORY', type=str, help='Directory to write output into.')
    parser.add_argument('--debug', action='store_true', help='Enable debug output.')

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    if not os.path.exists(args.out_dir):
        os.mkdir(args.out_dir)

    config = requests.get(HRS_URL + '/content/config/site_config.json').json()

    station_facts_url = '/content/json/{0}/{0}_station_attributes.json'
    for station in config['stations']['features']:
        station_id = station['properties']['AWRC_ID']
        get_url = HRS_URL + station_facts_url.format(station_id)
        logger.debug(get_url)
        station_facts = requests.get(get_url).json()
        with open(os.path.join(args.out_dir, station_id + '.json'), 'w') as f:
            logger.debug(station_id)
            json.dump(station_facts, f)
