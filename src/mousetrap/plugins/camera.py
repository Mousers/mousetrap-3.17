from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
import mousetrap.plugins.interface as interface


class CameraPlugin(interface.Plugin):
    def init(self):
        self.call(capture_image, on='clock_ticked')
        self.might_fire('captured_image')
        self._camera = self.grab_camera()

    def capture_image(self, event):
        image = self._camera.read_image()
        self.fire('captured_image', image=image)

    def grab_camera(self):
        from mousetrap.vision import Camera
        return Camera(self.app())
