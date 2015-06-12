from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from gi.repository import GLib

from mousetrap.lib import conf
from mousetrap.lib import Component


class CameraComponent(Component):
    def init(self):
        self.may_fire('captured_image')

    def start(self):
        GLib.timeout_add(conf[__name__]['capture_interval_milliseconds'], self.capture_image)

    def capture_image(self):
        if self.is_running():
            print('captured_image')
            self.fire('captured_image')
        return self.is_running()
