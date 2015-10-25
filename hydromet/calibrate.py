from scipy.optimize import differential_evolution

from hydromet.skillscore import kge, nse
from hydromet.system import get_model_config

def calibrate(project_dir, model, bounds, data, qobs):
    config = get_model_config(project_dir, model.name)
    model.init(
        config['warmup']['start_date'],
        config['warmup']['end_date'],
        config['calibration']['start_date'],
        config['calibration']['end_date']
    )

    result_nse = differential_evolution(model.obj_func, bounds, (data, qobs, nse), disp=True)

    return result_nse
