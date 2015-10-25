import yaml
from hydromet.disaggregate import monthly_to_daily

def load_model_config(filename):
    with open(filename) as yml_file:
        config = yaml.load(yml_file)

    return config

def read_predictors(db, config, station_id):
    predictor_config = config['predictors']
    predictors = {}
    for predictor, attrs in predictor_config.items():
        predictors[predictor] = __resample(db.read(station_id, attrs['source_freq'], **attrs['db_attrs']), attrs['source_freq'], attrs['model_freq'])

    return predictors

def __resample(series, source_freq, model_freq):
    if source_freq == model_freq:
        return series
    elif source_freq == 'MS' and model_freq == 'D':
        return monthly_to_daily(series)
    else:
        raise NotImplemented("Source frequency '{0}' can not be converted to model frequency '{1}' at this time.")
