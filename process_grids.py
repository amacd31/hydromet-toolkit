import glob
from hydromet.catchments import create_grids

grid_dir = 'data/hrs_geojson'
catchment_files = glob.glob(grid_dir + "/*.json")

catchments = []
for catchment in catchment_files:
    catchments.append(catchment.split('.')[0].replace(grid_dir+"/", ''))

create_grids(catchments, grid_dir, 'data/catchment_grids', 'data/awap_grid.asc')
