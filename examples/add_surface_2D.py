"""
Display a 2D surface
"""

import numpy as np
from skimage import data
import napari


with napari.gui_qt():
    data = np.array([[0, 0], [0, 20], [10, 0], [10, 10]])
    faces = np.array([[0, 1, 2], [1, 2, 3]])
    values = np.linspace(0, 1, len(data))

    # add the surface
    viewer = napari.add_surface((data, faces, values))
