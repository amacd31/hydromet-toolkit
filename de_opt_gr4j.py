import numpy as np
import json

from hydromet.models.gr4j_model import GR4J
from hydromet.calibrate import calibrate
from hydromet.disaggregate import monthly_to_daily
from hydromet.io import read_predictors
from hydromet.system import get_model_config

from phildb.database import PhilDB

db = PhilDB('hm_tsdb')
config = get_model_config('project', 'gr4j')

for station_id in ['410730']:
    area = np.loadtxt('data/catchment_grids/{0}.area'.format(station_id))
    q = db.read(station_id, 'D', source='BOM_HRS', measurand='Q') / area
    predictors = read_predictors(db, config, station_id)

    model = GR4J()

    bounds = [(10,1500), (-5, 5), (10, 900), (0,5)]
    results = []
    res_nse = calibrate('project', model, bounds, predictors, q)
    results.append({'efficiency': 1 - res_nse.fun,
            'efficiency_type': 'nse',
            'X1': res_nse.x[0],
            'X2': res_nse.x[1],
            'X3': res_nse.x[2],
            'X4': res_nse.x[3]
        }
    )

    print(results)

    json.dump(results, open('de_opt_{0}_params.json'.format(station_id),'w'))
