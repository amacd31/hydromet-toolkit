import pandas as pd
import zipfile
import bom_data_parser as bdp
from kiwis_pie import KIWIS
from phildb.exceptions import DuplicateError

def load_cdo(db, files):

    for f in files:
        data, metadata = bdp.read_climate_data_online_zip(f)

        station_id = '{0:06d}'.format(metadata['Bureau of Meteorology station number'])
        data_column_name = data.columns[0]
        if data_column_name == 'airtemp_max':
            measurand = 'T_MAX'
        elif data_column_name == 'airtemp_min':
            measurand = 'T_MIN'
        else:
            raise ValueError("Unknown CDO data type: '{0}'".format(data_column_name ))

        try:
            db.add_timeseries(station_id)
        except DuplicateError:
            pass

        try:
            db.add_source('BOM_CDO', 'Bureau of Meterology Climate Data Online')
        except DuplicateError:
            pass

        try:
            db.add_measurand('T_MAX', 'MAXIMUM_TEMPERATURE', 'Maximum Temperature')
        except DuplicateError:
            pass

        try:
            db.add_measurand('T_MIN', 'MINIMUM_TEMPERATURE', 'Minimum Temperature')
        except DuplicateError:
            pass

        try:
            db.add_timeseries_instance(station_id, 'D', '', source='BOM_CDO', measurand='T_MAX')
        except DuplicateError:
            pass

        try:
            db.add_timeseries_instance(station_id, 'D', '', source='BOM_CDO', measurand='T_MIN')
        except DuplicateError:
            pass

        print("Loading CDO zip {0} as {1} with measurand {2}".format(f, station_id, measurand))

        db.write(station_id, 'D', data[data_column_name], source='BOM_CDO', measurand=measurand)

def read_streamflow(station_id, from_date = '1900-01-01', to_date = '2100-01-01'):
    k = KIWIS('http://www.bom.gov.au/waterdata/services')

    ts_id = k.get_timeseries_list(
        station_no = station_id,
        ts_name = 'DMQaQc.Merged.DailyMean.09HR',
        return_fields = [
            'station_no',
            'ts_id',
            'ts_name',
            'parametertype_name'
        ]
    )['ts_id']

    if len(ts_id) != 1:
        # TODO: Specify which provider to use if more than one provider supplies
        # data for a given station. As opposed to just using the first available.
        ts_id = ts_id.iloc[0]

    sf = k.get_timeseries_values(
        ts_id = ts_id,
        to = to_date,
        return_fields = ['Timestamp', 'Value'],
        **{'from': from_date}
    )

    if len(sf) == 0:
        raise ValueError("No streamflow could be read.")

    # Remove the time component and move forward by a day because,
    # without the time/timezone all stations across Australian timezones fall
    # on the previous day. Adding one day pushes the daily data onto the correct day.
    sf.index = sf.index.normalize() + pd.DateOffset(days=1)

    return sf


def load_streamflow(db, station_no):

    sf = read_streamflow(station_no)

    try:
        db.add_timeseries(station_no)
    except DuplicateError:
        pass

    try:
        db.add_source('BOM_WISKI', 'Bureau of Meterology Water Data Online')
    except DuplicateError:
        pass

    try:
        db.add_measurand('Q', 'STREAMFLOW', 'Streamflow')
    except DuplicateError:
        pass

    try:
        db.add_timeseries_instance(station_no, 'D', '', source='BOM_WISKI', measurand='Q')
    except DuplicateError:
        pass

    db.write(station_no, 'D', sf, source='BOM_WISKI', measurand='Q')
