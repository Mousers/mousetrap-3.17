from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
import mousetrap.plugins.interface as interface


class DisplayPlugin(interface.Plugin):

    def init(self):
        self.call(self.display_image, on='captured_image')

    def display_image(self, event):
        title = self.config('window_title')
        self.app().gui.show_image(title, event['image'])
