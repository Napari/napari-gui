import sys
import warnings
from typing import List

import pytest

from napari.utils.notifications import (
    Notification,
    notification_manager,
    show_info,
)


def test_notification_manager_no_gui():
    """
    Direct test of the notification manager.

    This does not test the integration with the gui, but test that the
    notification manager itself can receive a info, warning or error.
    """

    previous_exhook = sys.excepthook
    with notification_manager:
        store: List[Notification] = []
        # save all of the events that get emitted
        notification_manager.notification_ready.connect(store.append)

        show_info('this is one way of showing an information message')
        assert len(notification_manager.records) == 1
        assert store[-1].type == 'info'

        notification_manager.receive_info(
            'This is another information message'
        )
        assert len(notification_manager.records) == 2
        assert store[-1].type == 'info'

        # test that exceptions that go through sys.excepthook are catalogued

        class PurposefulException(Exception):
            pass

        with pytest.raises(PurposefulException):
            raise PurposefulException("this is an exception")

        # pytest intercepts the error, so we can manually call sys.excepthook
        assert sys.excepthook == notification_manager.receive_error
        sys.excepthook(*sys.exc_info())
        assert len(notification_manager.records) == 3
        assert store[-1].type == 'error'

        # test that warnings that go through showwarning are catalogued
        # again, pytest intercepts this, so just manually trigger:
        assert warnings.showwarning == notification_manager.receive_warning
        warnings.showwarning('this is a warning', UserWarning, '', 0)
        assert len(notification_manager.records) == 4
        assert store[-1].type == 'warning'

    # make sure we've restored the except hook
    assert sys.excepthook == previous_exhook

    assert all(isinstance(x, Notification) for x in store)
