import os
import numpy as np

from catchment_cutter import get_grid_cells

def create_grids(catchments, in_directory, out_directory, grid_file):
    """
        Create grid files for the supplied catchments.

        :param catchments: List of catchment IDs.
        :type catchments: Array(string)
        :param in_directory: Path to catchment boundary (geojson) directory.
        :type in_directory: string
        :param out_directory: Output directory for catchment grid csv files.
        :type out_directory: string
        :param grid_file: Path to input grid file for coordinates to match boundaries against.
        :type grid_file: string
    """
    for catchment in catchments:
        boundary = os.path.join(in_directory, catchment + '.json')
        cells = np.asarray(get_grid_cells(boundary, grid_file))

        np.savetxt(os.path.join(out_directory, catchment + '.csv'), cells, fmt="%.2f", delimiter=',')

