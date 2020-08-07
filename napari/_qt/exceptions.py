import logging
import traceback
from enum import auto
from types import TracebackType
from typing import Callable, Sequence, Tuple, Type

from qtpy.QtCore import (
    QEasingCurve,
    QObject,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    QTimer,
    Signal,
)
from qtpy.QtGui import QFontMetrics, QPainter, QTextLayout
from qtpy.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from napari.utils.misc import StringEnum


class ExceptionHandler(QObject):
    """General class to handle all uncaught exceptions in the Qt event loop"""

    error = Signal(tuple)
    message = None

    def handle(
        self,
        etype: Type[BaseException],
        value: BaseException,
        tb: TracebackType,
    ):
        """Our sys.excepthook override.

        This function handles uncaught exceptions and can delegate to a
        secondary handler, whether it be a GUI dialog, or an IPython traceback
        printout.  The override to ``sys.excepthook`` happens in
        :func:`napari.gui_qt`, and therefore this is only active when the qt
        event loop has been started by napari.

        The three parameters here are what would be returned from
        :func:`sys.exc_info()`.

        Parameters
        ----------
        etype : Type[BaseException]
            The type of error raised
        value : BaseException
            The error instance
        tb : TracebackType
            The traceback object associated with the error.
        """
        # etype.__module__ contains the module raising the error
        # Custom exception classes can have different behavior
        # can add custom exception handlers here ...
        text = "".join(traceback.format_exception(etype, value, tb))
        logging.error("Unhandled exception:\n%s", text)
        self._show_error_dialog(value)
        self.error.emit((etype, value, tb))

    def _show_error_dialog(self, exception: BaseException):
        msg = """Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut
enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
aliquip ex ea commodo consequat.""".strip()

        self.message = NapariNotification(
            str(msg),
            actions=[('do something', lambda: print('hi'))],
            source='some plugin',
        )
        self.message.show()


class NotificationSeverity(StringEnum):
    ERROR = auto()
    WARNING = auto()
    INFO = auto()
    NONE = auto()

    def as_icon(self):
        return {
            self.ERROR: "‼️",
            self.WARNING: "⚠️",
            self.INFO: "ℹ️",
            self.NONE: "",
        }[self]


class NapariNotification(QDialog):
    MAX_OPACITY = 0.9
    FADE_IN_RATE = 220
    FADE_OUT_RATE = 120
    DISMISS_AFTER = 5000
    MIN_WIDTH = 400

    def __init__(
        self,
        message: str,
        severity: NotificationSeverity = NotificationSeverity.INFO,
        source: str = None,
        actions: Sequence[Tuple[str, Callable[[], None]]] = (),
    ):
        # FIXME: this works with command line, but not with IPython...
        # and may not work well with multiple viewers.
        parent = None
        for wdg in QApplication.topLevelWidgets():
            if isinstance(wdg, QMainWindow):
                parent = wdg
                break
        super().__init__(parent)
        if self.parent():
            self.parent().resized.connect(self.move_to_bottom_right)
        self.setWindowFlags(
            Qt.SubWindow | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setupUi()
        self.setup_buttons(actions)
        self.setMouseTracking(True)

        self.severity_icon.setText(severity.as_icon())
        self.message.setText(message)
        if source:
            self.source_label.setText(f'source: {source}')
        self.close_button.clicked.connect(self.close)
        self.expand_button.clicked.connect(self.expand)

        self.opacity = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity)
        self.opacity_anim = QPropertyAnimation(self.opacity, b"opacity", self)
        self.geom_anim = QPropertyAnimation(self, b"geometry", self)
        self.move_to_bottom_right()

    def move_to_bottom_right(self, size=None, from_edge=(22, 50)):
        # move to the bottom right of parent
        sz = (size or self.parent().size()) - self.size() - QSize(*from_edge)
        self.move(QPoint(sz.width(), sz.height()))

    def slide_in(self):
        # slide in
        geom = self.geometry()
        self.geom_anim.setDuration(self.FADE_IN_RATE)
        self.geom_anim.setStartValue(geom.translated(0, 20))
        self.geom_anim.setEndValue(geom)
        self.geom_anim.setEasingCurve(QEasingCurve.OutQuad)
        # fade in
        self.opacity_anim.setDuration(self.FADE_IN_RATE)
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(self.MAX_OPACITY)
        self.geom_anim.start()
        self.opacity_anim.start()

    def show(self):
        """Show the message with a fade and slight slide in from the bottom.
        """
        super().show()
        self.slide_in()
        self.timer = QTimer()
        self.timer.setInterval(self.DISMISS_AFTER)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.close)
        self.timer.start()

    def mouseMoveEvent(self, event):
        self.close_button.show()
        self.timer.stop()

    def close(self):
        """Fade out then close."""
        self.opacity_anim.setDuration(self.FADE_OUT_RATE)
        self.opacity_anim.setStartValue(self.MAX_OPACITY)
        self.opacity_anim.setEndValue(0)
        self.opacity_anim.start()
        self.opacity_anim.finished.connect(super().close)

    def expand(self):
        curr = self.geometry()
        self.geom_anim.setDuration(100)
        self.geom_anim.setStartValue(curr)
        new_height = self.sizeHint().height()
        delta = new_height - curr.height()
        self.geom_anim.setEndValue(
            QRect(curr.x(), curr.y() - delta, curr.width(), new_height)
        )
        self.geom_anim.setEasingCurve(QEasingCurve.OutQuad)
        self.geom_anim.start()
        self.expand_button.clicked.disconnect(self.expand)
        self.expand_button.clicked.connect(self.contract)
        self.setProperty('expanded', "true")
        self.style().unpolish(self.expand_button)
        self.style().polish(self.expand_button)

    def contract(self):
        geom = self.geometry()
        self.geom_anim.setDuration(100)
        self.geom_anim.setStartValue(geom)
        dlt = geom.height() - self.minimumHeight()
        self.geom_anim.setEndValue(
            QRect(geom.x(), geom.y() + dlt, geom.width(), geom.height() - dlt)
        )
        self.geom_anim.setEasingCurve(QEasingCurve.OutQuad)
        self.geom_anim.start()
        self.expand_button.clicked.disconnect(self.contract)
        self.expand_button.clicked.connect(self.expand)
        self.setProperty('expanded', "false")
        self.style().unpolish(self.expand_button)
        self.style().polish(self.expand_button)

    def setupUi(self):
        self.setMinimumWidth(self.MIN_WIDTH)
        self.setMinimumHeight(40)
        self.setSizeGripEnabled(False)
        self.setModal(False)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setSpacing(0)

        self.row1_widget = QWidget(self)
        self.row1 = QHBoxLayout(self.row1_widget)
        self.row1.setContentsMargins(12, 12, 12, 8)
        self.row1.setSpacing(4)
        self.severity_icon = QLabel(self.row1_widget)
        self.severity_icon.setMinimumWidth(30)
        self.severity_icon.setMaximumWidth(30)
        self.row1.addWidget(self.severity_icon, alignment=Qt.AlignTop)
        self.message = MultilineElidedLabel(self.row1_widget)
        self.message.setMinimumWidth(self.MIN_WIDTH - 200)
        self.message.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.row1.addWidget(self.message, alignment=Qt.AlignTop)
        self.expand_button = QPushButton(self.row1_widget)
        self.expand_button.setObjectName("expand_button")
        self.expand_button.setMaximumWidth(20)
        self.expand_button.setFlat(True)

        self.row1.addWidget(self.expand_button, alignment=Qt.AlignTop)
        self.close_button = QPushButton(self.row1_widget)
        self.close_button.setObjectName("close_button")
        self.close_button.setMaximumWidth(20)
        self.close_button.setFlat(True)

        self.row1.addWidget(self.close_button, alignment=Qt.AlignTop)
        self.verticalLayout.addWidget(self.row1_widget, 1)
        self.row2_widget = QWidget(self)
        self.row2_widget.hide()
        self.row2 = QHBoxLayout(self.row2_widget)
        self.source_label = QLabel(self.row2_widget)
        self.source_label.setObjectName("source_label")
        self.row2.addWidget(self.source_label, alignment=Qt.AlignBottom)
        self.row2.addStretch()
        self.row2.setContentsMargins(12, 2, 16, 12)
        self.row2_widget.setMaximumHeight(34)
        self.row2_widget.setStyleSheet(
            'QPushButton{'
            'padding: 4px 12px 4px 12px; '
            'font-size: 11px;'
            'min-height: 18px; border-radius: 0;}'
        )
        self.verticalLayout.addWidget(self.row2_widget, 0)
        self.setProperty('expanded', "false")

    def setup_buttons(self, actions=()):
        for text, callback in actions:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            btn.clicked.connect(self.close)
            self.row2.addWidget(btn)
        if actions:
            self.row2_widget.show()
            self.setMinimumHeight(
                self.row2_widget.maximumHeight() + self.minimumHeight()
            )

    def sizeHint(self):
        return QSize(
            super().sizeHint().width(),
            self.row2_widget.height() + self.message.sizeHint().height(),
        )


class MultilineElidedLabel(QFrame):
    def __init__(self, parent=None, text=''):
        super().__init__(parent)
        self.setText(text)

    def setText(self, text=None):
        if text is not None:
            self._text = text
        self.update()
        self.adjustSize()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        font_metrics = painter.fontMetrics()
        text_layout = QTextLayout(self._text, painter.font())
        text_layout.beginLayout()

        y = 0
        while True:
            line = text_layout.createLine()
            if not line.isValid():
                break
            line.setLineWidth(self.width())
            nextLineY = y + font_metrics.lineSpacing()
            if self.height() >= nextLineY + font_metrics.lineSpacing():
                line.draw(painter, QPoint(0, y))
                y = nextLineY
            else:
                lastLine = self._text[line.textStart() :]
                elidedLastLine = font_metrics.elidedText(
                    lastLine, Qt.ElideRight, self.width()
                )
                painter.drawText(
                    QPoint(0, y + font_metrics.ascent()), elidedLastLine
                )
                line = text_layout.createLine()
                break
        text_layout.endLayout()

    def sizeHint(self):
        font_metrics = QFontMetrics(self.font())
        r = font_metrics.boundingRect(
            QRect(QPoint(0, 0), self.size()),
            Qt.TextWordWrap | Qt.ElideRight,
            self._text,
        )
        return QSize(self.width(), r.height())
