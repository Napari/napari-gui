from qtpy.QtWidgets import QDockWidget

import napari.layers


def test_add_function_widget(make_test_viewer):
    """Test basic add_function_widget functionality"""
    viewer = make_test_viewer()

    # Define a function.
    def image_sum(
        layerA: napari.layers.Image, layerB: napari.layers.Image
    ) -> napari.layers.Image:
        """Add two layers."""
        return layerA.data + layerB.data

    # Define magicgui keyword arguments
    magic = {'call_button': "execute"}

    dwidg = viewer.window.add_function_widget(image_sum, magic_kwargs=magic)
    assert dwidg.name == 'image sum'
    assert viewer.window._qt_window.findChild(QDockWidget, 'image sum')
