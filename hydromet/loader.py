import zipfile
import bom_data_parser as bdp
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

