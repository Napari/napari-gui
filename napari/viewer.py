from .components._viewer.view import QtViewer
from .components import Window, ViewerModel


class Viewer(ViewerModel):
    """Napari ndarray viewer.

    Parameters
    ----------
    title : string
        The title of the viewer window.
    """

    def __init__(self, title='napari', hide_menubar=True):
        super().__init__(title=title)
        qt_viewer = QtViewer(self)
        self.window = Window(qt_viewer, hide_menubar=hide_menubar)
        self.screenshot = self.window.qt_viewer.screenshot
        self.camera = self.window.qt_viewer.view.camera
