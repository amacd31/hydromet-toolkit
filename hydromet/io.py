import numpy as np
import yaml
from hydromet.disaggregate import monthly_to_daily

def load_model_config(filename):
    with open(filename) as yml_file:
        config = yaml.load(yml_file)

    return config

def get_idx(config, typ):
    if typ is None:
        idx = slice()
    else:
        idx = slice(config[typ]['start_date'], config[typ]['end_date'])

    return idx

def read_predictors(db, config, station_id, typ = None, idx = None):
    if idx is None:
        idx = get_idx(config, typ)
    return __read_predict(db, config['predictors'], station_id, idx)

def read_predictands(db, config, station_id, typ = None, idx = None):
    if idx is None:
        idx = get_idx(config, typ)
    return __read_predict(db, config['predictands'], station_id, idx)

def __read_predict(db, config, station_id, idx):
    predicts = {}
    for predict, attrs in config.items():
        predicts[predict] = __resample(db.read(station_id, attrs['source_freq'], **attrs['db_attrs']), attrs['source_freq'], attrs['model_freq']).ix[idx]

    return predicts

def __resample(series, source_freq, model_freq, how = 'sum'):
    if source_freq == model_freq:
        return series
    elif source_freq == 'MS' and model_freq == 'D':
        return monthly_to_daily(series)
    elif source_freq == 'D' and model_freq == 'MS':
        return series.resample(model_freq, how = how)
    else:
        raise NotImplementedError("Source frequency '{0}' can not be converted to model frequency '{1}' at this time.".format(source_freq, model_freq))
