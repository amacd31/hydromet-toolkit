import os
import hydromet.io

def get_model_dir(project_dir, model_name):
    return os.path.join(project_dir, 'models', model_name)

def get_model_config(project_dir, model_name):
    filename = os.path.join(get_model_dir(project_dir, model_name), 'common_config.yml')
    return hydromet.io.load_model_config(filename)
