from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
import unittest
from mousetrap.vision import Camera
from mousetrap.main import Config


class test_camera(unittest.TestCase):

    def setUp(self):
        self.camera = Camera(Config().load_default())


if __name__ == '__main__':
    unittest.main()
