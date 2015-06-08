from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
import logging
LOGGER = logging.getLogger(__name__)
from mousetrap.i18n import _


from mousetrap.gui import Pointer
class PointerComponent(Component):
    def init(self):
        self._pointer = Pointer()
        self.call(self.move, on='move_pointer')
        self.call(self.warp, on='warp_pointer')

    def move(self, event):
        m = self.config()['multiplier']
        dx = event['dx']
        dy = event['dy']
        self._pointer.move(int(m*dx), int(m*dy))

    def warp(self, event):
        x = event['x']
        y = event['y']
        self._pointer.warp(x, y)


from mousetrap.gui import Gui
class GuiComponent(Component):
    def init(self):
        self._gui = Gui()

    def start(self):
        self._gui.start()

    def stop(self):
        self._gui.stop()


from gi.repository import GLib
class Loop(Component):
    MILLISECONDS_PER_SECOND = 1000.0
    CALLBACK_RUN = 'run'

    def init(self):
        self._interval = None
        self._loops_per_second = None
        self._timeout_id = None
        self._set_loops_per_second(self.config()['loops_per_second'])
        self._loop_enabled = True

    def _set_loops_per_second(self, loops_per_second):
        self._loops_per_second = loops_per_second
        self._interval = int(round(
            self.MILLISECONDS_PER_SECOND / self._loops_per_second))

    def start(self):
        self._timeout_id = GLib.timeout_add(self._interval, self._run)

    def stop(self):
        self._loop_enabled = False

    def _run(self):
        if self._loop_enabled:
            self.fire('loop_ticked')
        return self._loop_enabled
