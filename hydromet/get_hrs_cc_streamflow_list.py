import pandas as pd
from kiwis_pie import KIWIS

k = KIWIS('http://www.bom.gov.au/waterdata/services')

def get_cc_hrs_station_list(update = False):
    """
        Return list of station IDs that exist in HRS and are supplied by providers that license their data under the Creative Commons license.

        :param update: Flag to indicate if cached station information should be fetched from WISKI again (and saved to disk as CSV).
        :type update: boolean
    """
    if update:
        stations = k.get_timeseries_list(parametertype_name = 'Water Course Discharge', ts_name = 'DMQaQc.Merged.DailyMean.09HR')
        stations.to_csv('available_watercoursedischarge_stations.csv')
    else:
        stations = pd.read_csv('available_watercoursedischarge_stations.csv', index_col=0)

    hrs_stations = pd.read_csv('hrs_station_list.csv', skiprows=1)

    station_subset = stations.ix[stations.station_no.isin(hrs_stations.station_id)]

    if update:
        station_attrs = []
        for i, station in station_subset.iterrows():
            attrs = k.get_station_list(station_no = station.station_no, parametertype_name = 'Water Course Discharge', return_fields=['station_id','custom_attributes'])
            station_attrs.append(attrs.set_index('station_id'))

        station_attributes = pd.concat(station_attrs)
        station_attributes.to_csv('station_attributes.csv')
    else:
        station_attributes = pd.read_csv('station_attributes.csv', index_col=0)

    cc_providers = pd.read_csv('cc_providers.csv', skiprows=8)

    station_list = station_attributes.ix[station_attributes.DATA_OWNER.isin(cc_providers.ProviderID.values)].index.values

    return station_list

if __name__ == "__main__":
    for station in get_cc_hrs_station_list():
        print(station)

