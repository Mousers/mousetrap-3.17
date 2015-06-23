from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import mousetrap.plugins.interface as interface
from mousetrap.vision import FeatureDetector, FeatureNotFoundException
from mousetrap.gui import Gui


class NosePlugin(interface.Plugin):
    def __init__(self, config):
        self._config = config
        self._nose_locator = NoseLocator()
        self._gui = Gui()
        self._location = None
        self._image = None

    def update_image(self, image):
        self._image = image
        try:
            point_image = self._nose_locator.locate(image)
            point_screen = self._convert_image_to_screen_point(*point_image)
            self._location = point_screen
        except FeatureNotFoundException:
            self._location = None

    def _convert_image_to_screen_point(self, image_x, image_y):
        image_width = self._image.get_width()
        image_height = self._image.get_height()
        percent_x = 1.0 * image_x // image_width
        percent_y = 1.0 * image_y // image_height
        screen_x = percent_x * self._gui.get_screen_width()
        screen_y = percent_y * self._gui.get_screen_height()
        half_width = self._gui.get_screen_width() // 2
        screen_x = (-1 * (screen_x - half_width)) + half_width
        return (screen_x, screen_y)

    def get_new_position(self):
        return self._location


class NoseJoystickPlugin(interface.Plugin):

    def __init__(self, config):
        self._config = config
        self._threshold = config[self]['threshold']
        self._nose_locator = NoseLocator(config)
        self._initial_image_location = (0, 0)
        self._last_delta = (0, 0)

    def run(self, app):
        self._app = app
        try:
            point_image = self._nose_locator.locate(app.image)
            delta = self._convert_image_to_pointer_delta(*point_image)
        except FeatureNotFoundException:
            delta = self._last_delta
        app.pointer.move(delta)

    def _convert_image_to_pointer_delta(self, image_x, image_y):
        initial_x, initial_y = self._initial_image_location

        if initial_x == 0 and initial_y == 0:
            self._initial_image_location = (image_x, image_y)

            return self._initial_image_location

        delta_x = initial_x - image_x
        delta_y = image_y - initial_y

        if abs(delta_x) < self._threshold:
            delta_x = 0

        if abs(delta_y) < self._threshold:
            delta_y = 0

        delta = (delta_x, delta_y)

        self._last_delta = delta

        return delta


class NoseLocator(object):
    def __init__(self, config):
        self._config = config
        self._face_detector = FeatureDetector.get_detector(
            config,
            'face',
            scale_factor=config[self]['face_detector']['scale_factor'],
            min_neighbors=config[self]['face_detector']['min_neighbors'],
        )
        self._nose_detector = FeatureDetector.get_detector(
            config,
            'nose',
            scale_factor=config[self]['nose_detector']['scale_factor'],
            min_neighbors=config[self]['nose_detector']['min_neighbors'],
        )

    def locate(self, image):
        face = self._face_detector.detect(image)
        nose = self._nose_detector.detect(face['image'])
        return (
            face['x'] + nose['center']['x'],
            face['y'] + nose['center']['y'],
        )
