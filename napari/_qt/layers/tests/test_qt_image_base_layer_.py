import numpy as np
import pytest
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QPushButton

from napari.layers import Image, Surface
from napari._qt.layers.qt_image_base_layer import QtBaseImageControls


@pytest.mark.parametrize('model', [Image, Surface])
def test_base_controls_contrast_limits(qtbot, model):
    if model == Image:
        data = np.arange(100).astype(np.uint16).reshape((10, 10))
    elif model == Surface:
        vertices = np.random.random((10, 2))
        faces = np.random.randint(10, size=(6, 3))
        values = np.arange(100).astype(np.float)
        data = (vertices, faces, values)
    layer = model(data)

    # create base layer controls
    qtctrl = QtBaseImageControls(layer)
    original_clims = tuple(layer.contrast_limits)
    slider_clims = qtctrl.contrastLimitsSlider.values()
    assert slider_clims[0] == 0
    assert slider_clims[1] == 99
    assert tuple(slider_clims) == original_clims

    # right clicking brings up the contrast limits menu
    qtbot.mousePress(qtctrl.contrastLimitsSlider, Qt.RightButton)
    assert hasattr(qtctrl, 'clim_pop')
    assert qtctrl.clim_pop.isVisible()

    # changing the model updates the view
    new_clims = (20, 40)
    layer.contrast_limits = new_clims
    assert tuple(qtctrl.contrastLimitsSlider.values()) == new_clims

    # pressing the reset button returns the clims to the default values
    reset_button = qtctrl.clim_pop.findChild(QPushButton, "reset_clims_button")
    qtbot.mouseClick(reset_button, Qt.LeftButton)
    assert tuple(qtctrl.contrastLimitsSlider.values()) == original_clims

    rangebtn = qtctrl.clim_pop.findChild(QPushButton, "full_clim_range_button")
    # the data we created above was uint16 for Image, and float for Surface
    # Surface will not have a "full range button"
    if model == Image:
        qtbot.mouseClick(rangebtn, Qt.LeftButton)
        assert tuple(layer.contrast_limits_range) == (0, 2 ** 16 - 1)
        assert tuple(qtctrl.contrastLimitsSlider.range) == (0, 2 ** 16 - 1)
    else:
        assert rangebtn is None
