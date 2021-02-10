"""
This module tests our "pytest plugin" made available in
``napari.utils._testsupport``.  It's here in the top level `_tests` folder
because it requires qt, and should be omitted from headless tests.
"""

import pytest

pytest_plugins = "pytester"


@pytest.mark.filterwarnings("ignore:`type` argument to addoption()::")
@pytest.mark.filterwarnings("ignore:The TerminalReporter.writer::")
def test_make_napari_viewer(testdir):
    """Make sure that our make_napari_viewer plugin works."""

    # create a temporary pytest test file
    testdir.makepyfile(
        """
        def test_make_viewer(make_napari_viewer):
            viewer = make_napari_viewer()
            assert viewer.layers == []
            assert viewer.__class__.__name__ == 'Viewer'
            assert not viewer.window._qt_window.isVisible()

    """
    )
    # run all tests with pytest
    result = testdir.runpytest()

    # check that all 1 test passed
    result.assert_outcomes(passed=1)


def test_napari_plugin_tester(testdir):
    """Make sure that our napari_plugin_tester fixture works."""

    # create a temporary pytest test file
    testdir.makepyfile(
        """
        from napari_plugin_engine import napari_hook_implementation
        class Plugin:

            @napari_hook_implementation
            def napari_get_reader(path):
                pass

        def test_pm(napari_plugin_tester):
            napari_plugin_tester.register(Plugin)
            napari_plugin_tester.assert_plugin_name_registered("Plugin")
            napari_plugin_tester.assert_module_registered(Plugin)
            napari_plugin_tester.assert_implementations_registered(
                Plugin, "napari_get_reader"
            )
    """
    )
    # run all tests with pytest
    result = testdir.runpytest()

    # check that all 1 test passed
    result.assert_outcomes(passed=1)
