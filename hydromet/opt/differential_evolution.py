import argparse
import os
import timeit
import pandas as pd
import numpy as np
import pyopencl as cl
from tsdb.database import TSDB
from gr4j import gr4j
import sys

from hydromet import disaggregate as d
from hydromet.skillscore import kge, nse, mse, rmse

iterations = 10000

def load_data(station_id, db, catchment_area):

    p = db.read(station_id, 'D', measurand='P', source = 'BOM_AWAP').ix['1970':'2000'].values
    pe = d.monthly_to_daily(db.read(station_id, 'MS', measurand='PE', source = 'CSIRO_AWAP_26J')).ix['1970':'2000'].values
    sf = db.read(station_id, 'D', measurand='Q', source = 'BOM_HRS').ix['1970':'2000'].values / catchment_area

    return p.astype(np.float32), pe.astype(np.float32), sf.astype(np.float32)

def opencl(p, pet, obs, params):
    platform = cl.get_platforms()
    gpus = platform[0].get_devices(device_type=cl.device_type.GPU)

    ctx = cl.Context(devices=gpus)
    queue = cl.CommandQueue(ctx)

    mf = cl.mem_flags
    p_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=p)
    pet_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=pet)
    obs_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=obs)


    res_np = np.zeros((iterations * len(p))).astype(np.float32)
    ss_np = np.zeros(iterations).astype(np.float32)

    X1_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=params['X1'].values)
    X2_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=params['X2'].values)
    X3_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=params['X3'].values)
    X4_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=params['X4'].values)

    with open(os.path.join(os.path.dirname(__file__), 'gr4j.cl')) as code_file:
        code = code_file.read()

    prg = cl.Program(ctx, code).build()

    res_g = cl.Buffer(ctx, mf.WRITE_ONLY, res_np.nbytes)
    ss_g = cl.Buffer(ctx, mf.WRITE_ONLY, res_np.nbytes)
    prg.gr4j(queue, params['X1'].values.shape, None, p_g, pet_g, np.int32(len(p)), X1_g, X2_g, X3_g, X4_g, obs_g, ss_g, res_g)

    cl.enqueue_copy(queue, res_np, res_g)
    cl.enqueue_copy(queue, ss_np, ss_g)

    return res_np, ss_np

def diff_evolve(station_id, db, out_file, catchment_area):
    """
        Differential Evolution optimisation.

        :references:
            "Differential Evolution." Wikipedia, the Free Encyclopedia, April 3, 2015. http://en.wikipedia.org/w/index.php?title=Differential_evolution&oldid=654802241.
            Storn, Rainer. "Differential Evolution Homepage." Accessed May 2, 2015. http://www1.icsi.berkeley.edu/~storn/code.html.

            Storn, Rainer. "On the Usage of Differential Evolution for Function Optimization." In Fuzzy Information Processing Society, 1996. NAFIPS., 1996 Biennial Conference of the North American, 519-23. IEEE, 1996. http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=534789.

            Perrin, Charles, Claude Michel, and Vazken Andreassian. "Improvement of a Parsimonious Model for Streamflow Simulation." Journal of Hydrology 279, no. 1-4 (August 25, 2003): 275-89. doi:10.1016/S0022-1694(03)00225-7.
    """
    np.random.seed(1)

    p, pet, sf = load_data(station_id, db, catchment_area)

    bounds = {
        'X1': (0,2000),
        'X2': (-10,5),
        'X3': (1,500),
        'X4': (0.5,10),
    }

    initial_params = {}
    initial_params['X1'] = np.array(np.random.uniform(bounds['X1'][0], bounds['X1'][1],iterations)).astype(np.float32)
    initial_params['X2'] = np.array(np.random.uniform(bounds['X2'][0], bounds['X2'][1],iterations)).astype(np.float32)
    initial_params['X3'] = np.array(np.random.uniform(bounds['X3'][0], bounds['X3'][1],iterations)).astype(np.float32)
    initial_params['X4'] = np.array(np.random.uniform(bounds['X4'][0], bounds['X4'][1],iterations)).astype(np.float32)

    params = pd.DataFrame(initial_params)

    candidate_params = {}
    candidate_params['X1'] = np.array(np.random.uniform(bounds['X1'][0], bounds['X1'][1],iterations)).astype(np.float32)
    candidate_params['X2'] = np.array(np.random.uniform(bounds['X2'][0], bounds['X2'][1],iterations)).astype(np.float32)
    candidate_params['X3'] = np.array(np.random.uniform(bounds['X3'][0], bounds['X3'][1],iterations)).astype(np.float32)
    candidate_params['X4'] = np.array(np.random.uniform(bounds['X4'][0], bounds['X4'][1],iterations)).astype(np.float32)
    candidate_params = pd.DataFrame(candidate_params)

    diff_weight = 1.8
    crossover_prob = 0.8
    for i in range(200):
        crossover_prob = np.random.uniform(0.5, 1.0)
        initial_pop, initial_scores = opencl(p, pet, sf, params)
        initial_pop = initial_pop.reshape([iterations, len(p)])

        candidate_pop, candidate_scores = opencl(p, pet, sf, candidate_params.astype(np.float32))
        candiate_pop = candidate_pop.reshape([iterations, len(p)])

        better_scores = np.array(candidate_scores) < np.array(initial_scores)
        if i % 20 == 0:
            print len(params[better_scores]), min(candidate_scores), min(initial_scores), np.nanmean(candidate_scores), np.nanmean(initial_scores)

        params[better_scores] = candidate_params[better_scores]

        crossovers = np.random.uniform(size = params.shape[0]) % 1 < crossover_prob
        for col in params.columns:
            p1 = candidate_params[col][crossovers].copy()
            p2 = candidate_params[col][crossovers].copy()
            np.random.shuffle(p1.values)
            np.random.shuffle(p2.values)

            candidate_params.loc[crossovers, col] += diff_weight * (p1 - p2)

            under_idx = candidate_params[col] < bounds[col][0]
            under_idx_len = len(under_idx[under_idx == True])

            over_idx = candidate_params[col] > bounds[col][1]
            over_idx_len = len(over_idx[over_idx == True])

            candidate_params.loc[over_idx, col] = np.array(np.random.uniform(bounds[col][0], bounds[col][1],over_idx_len)).astype(np.float32)

            candidate_params.loc[under_idx, col] = np.array(np.random.uniform(bounds[col][0], bounds[col][1],under_idx_len)).astype(np.float32)

    params.to_json(out_file)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Search for optimal GR4J parameter sets.')
    parser.add_argument('station_id', type=str,
                        help='ID of station to load data for and optimise.')

    parser.add_argument('catchment_area', type=str,
                        help='Square km area of catchment (for converting runoff to mm).')

    parser.add_argument('--tsdb-name', type=str,
                        default = 'hm_tsdb',
                        help='TSDB to load the data from.')

    args = parser.parse_args()
    db = TSDB(args.tsdb_name)
    diff_evolve(args.station_id, db, "{0}_params.json".format(args.station_id), args.catchment_area)

