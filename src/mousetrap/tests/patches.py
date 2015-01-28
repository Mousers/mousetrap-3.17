from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


try:
    # Python 3
    import unittest.mock as mock
except ImportError:
    # Python 2
    import mock


class GtkGdkPatch:
    def __init__(self):
        self.patchers = {}
        self.mocks = {}

    def patch_in_setup(self, test_case):
        self._patch('gtk', test_case)
        self._patch('gdk', test_case)

    def _patch(self, thing, test_case):
        self.patchers[thing] = mock.patch('mousetrap.gui.' + thing)
        self.mocks[thing] = self.patchers[thing].start()
        test_case.addCleanup(self.patchers[thing].stop)
