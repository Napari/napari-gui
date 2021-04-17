import inspect
from typing import Iterable, Optional

from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QWidget,
)

from .._qt.utils import get_viewer_instance


def get_pbar():
    pbar = ProgressBar()
    viewer_instance = get_viewer_instance()
    viewer_instance.activityDock.widget().layout.addWidget(pbar.baseWidget)

    return pbar


def get_calling_function_name(max_depth: int):
    """Inspect stack up to max_depth and return first function name outside of progress.py"""
    for finfo in inspect.stack()[2:max_depth]:
        if not finfo.filename.endswith("progress.py"):
            return finfo.function

    return None


class progress:
    def __init__(
        self,
        iterable: Optional[Iterable] = None,
        desc: Optional[str] = None,
        total: Optional[int] = None,
        step: Optional[int] = None,
    ) -> None:
        self._iterable = iterable
        self._pbar = get_pbar()
        self.n = 0

        if iterable is not None:  # iterator takes priority over total
            try:
                self._total = len(iterable) - 1
            except TypeError:  # generator (total needed)
                self._total = total if total is not None else 0
        else:
            if total is not None:
                self._total = total
                # TODO: figure out the half open range thing...
                self._step = step if step else 1
                self._iterable = range(0, total + 1, self._step)
            else:
                self._total = 0
                self._step = 0

        self._pbar._set_total(self._total)

        if desc:
            self._pbar._set_description(desc)
        else:
            desc = get_calling_function_name(max_depth=5)
            if desc:
                self._pbar._set_description(desc)

        QApplication.processEvents()

    def __iter__(self):
        iterable = self._iterable
        n = self.n
        try:
            for obj in iterable:
                yield obj

                n += 1
                self.update(n)
        finally:
            self.n = n
            self.close()

    def __len__(self):
        if self._iterable is None:
            return self._total
        elif hasattr(self._iterable, 'shape'):
            return self._iterable.shape[0]
        elif hasattr(self._iterable, '__len__'):
            return len(self._iterable)
        else:
            return None

    def increment(self):
        """Increment progress bar using current step"""
        self._pbar._set_value(
            min(self._total, self._pbar._get_value() + self._step)
        )

    def decrement(self):
        """Decrement progress bar using current step"""
        self._pbar._set_value(max(0, self._pbar._get_value() - self._step))

    def update(self, val):
        """Update progress bar with new value

        Parameters
        ----------
        val : int
            new value for progress bar
        """
        if val > self._total:
            # exceeded total, become indeterminate
            self._pbar._set_total(0)
        else:
            self._pbar._set_value(val)

        QApplication.processEvents()

    def set_description(self, desc):
        """Update progress bar description"""
        self._pbar._set_description(desc)

    def hide(self):
        """Hide the progress bar"""
        self._pbar.baseWidget.hide()

    def show(self):
        """Show the progress bar"""
        self._pbar.baseWidget.show()

    def close(self):
        """Closes and deletes the progress bar widget"""
        self._pbar.baseWidget.close()


class ProgressBar:
    def __init__(self) -> None:
        self.baseWidget = QWidget()
        self.baseWidget.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.pbar = QProgressBar()
        self.label = QLabel()

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.pbar)
        self.baseWidget.setLayout(layout)

    def _set_total(self, total):
        if total > 0:
            self.pbar.setMaximum(total)
        else:
            self.pbar.setRange(0, 0)

    def _set_value(self, value):
        self.pbar.setValue(value)

    def _get_value(self):
        return self.pbar.value()

    def _set_description(self, desc):
        self.label.setText(desc)
