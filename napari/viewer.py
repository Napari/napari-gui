from os.path import dirname, join

from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QApplication

from napari._qt.qt_update_ui import QtUpdateUI

from ._qt.qt_main_window import Window
from ._qt.qt_viewer import QtViewer
from .components import ViewerModel


class Viewer(ViewerModel):
    """Napari ndarray viewer.

    Parameters
    ----------
    title : string
        The title of the viewer window.
    ndisplay : {2, 3}
        Number of displayed dimensions.
    order : tuple of int
        Order in which dimensions are displayed where the last two or last
        three dimensions correspond to row x column or plane x row x column if
        ndisplay is 2 or 3.
    axis_labels : list of str
        Dimension names.
    """

    def __init__(
        self, title='napari', ndisplay=2, order=None, axis_labels=None
    ):
        # instance() returns the singleton instance if it exists, or None
        app = QApplication.instance()
        # if None, raise a RuntimeError with the appropriate message
        if app is None:
            message = (
                "napari requires a Qt event loop to run. To create one, "
                "try one of the following: \n"
                "  - use the `napari.gui_qt()` context manager. See "
                "https://github.com/napari/napari/tree/master/examples for"
                " usage examples.\n"
                "  - In IPython or a local Jupyter instance, use the "
                "`%gui qt` magic command.\n"
                "  - Launch IPython with the option `--gui=qt`.\n"
                "  - (recommended) in your IPython configuration file, add"
                " or uncomment the line `c.TerminalIPythonApp.gui = 'qt'`."
                " Then, restart IPython."
            )
            raise RuntimeError(message)

        logopath = join(dirname(__file__), 'resources', 'logo.png')
        app.setWindowIcon(QIcon(logopath))

        super().__init__(
            title=title,
            ndisplay=ndisplay,
            order=order,
            axis_labels=axis_labels,
        )
        qt_viewer = QtViewer(self)
        self.window = Window(qt_viewer)
        self.update_console = self.window.qt_viewer.console.push

    def screenshot(self, with_viewer=False, max_shape=None):
        """Take currently displayed screen and convert to an image array.

        Parameters
        ----------
        with_viewer : bool
            If True includes the napari viewer, otherwise just includes the
            canvas.
        max_shape : int
            Size to which to rescale the largest axis. Only used without
            viewer (with_viewer = False).

        Returns
        -------
        image : array
            Numpy array of type ubyte and shape (h, w, 4). Index [0, 0] is the
            upper-left corner of the rendered region.
        """
        if with_viewer:
            image = self.window.screenshot()

        else:
            # capture initial canvas size to reset after screenshot
            canvas_size = self.window.qt_viewer.canvas.size
            if max_shape:
                if canvas_size[0] > canvas_size[1]:
                    new_shape = (
                        max_shape,
                        int(canvas_size[1] * max_shape / canvas_size[0]),
                    )
                else:
                    new_shape = (
                        int(canvas_size[0] * max_shape / canvas_size[1]),
                        max_shape,
                    )
                self.window.qt_viewer.canvas.size = new_shape

            image = self.window.qt_viewer.screenshot()
            self.window.qt_viewer.canvas.size = canvas_size

        return image

    def update(self, func, *args, **kwargs):
        t = QtUpdateUI(func, *args, **kwargs)
        self.window.qt_viewer.pool.start(t)
        return self.window.qt_viewer.pool  # returns threadpool object
