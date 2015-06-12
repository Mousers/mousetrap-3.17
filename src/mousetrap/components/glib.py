from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from gi.repository import GLib

from mousetrap.lib import Component


class GlibLoopComponent(Component):
    def init(self):
        self._glib_loop = GLib.MainLoop()

    def start(self):
        self._glib_loop.run()

    def stop(self):
        self._glib_loop.quit()
