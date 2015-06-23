from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
import unittest

try:
    # Python 3
    import unittest.mock as mock
except ImportError:
    # Python 2
    import mock

from mousetrap.main import Config
from .patches import GtkGdkPatch


class test_pointer(unittest.TestCase):

    def setUp(self):
        self.gtk_gdk_patcher = GtkGdkPatch()
        self.gtk_gdk_patcher.patch_in_setup(test_case=self)

        from mousetrap.gui import Pointer
        self.pointer = Pointer(Config().load_default())

    def test_get_position(self):
        pointer_x, pointer_y = self.pointer.get_position()

        try:
            pointer_x += 1
            pointer_y += 1
        except TypeError:
            self.assertTrue(
                False,
                msg='pointer_x or pointer_y is not a number'
            )

    def test_set_position(self):
        self.pointer.get_position = mock.Mock(return_value=(3, 4))
        self.pointer.set_position((3, 4))
        pointer_x, pointer_y = self.pointer.get_position()
        self.assertEquals(3, pointer_x)
        self.assertEquals(4, pointer_y)

    def test_move(self):
        self.pointer.get_position = mock.Mock(return_value=(2, 2))
        self.pointer.set_position = mock.Mock()
        self.pointer.move((1, 1))
        self.pointer.set_position.assert_called_with((3, 3))

    def test_move_negative(self):
        self.pointer.get_position = mock.Mock(return_value=(100, 50))
        self.pointer.set_position = mock.Mock()
        self.pointer.move((-10, -5))
        self.pointer.set_position.assert_called_with((90, 45))

    def test_move_with_multiplier(self):
        self.pointer.set_move_multiplier(3)
        self.pointer.get_position = mock.Mock(return_value=(2, 3))
        self.pointer.set_position = mock.Mock()
        self.pointer.move((2, 2))
        new_x = 2 + (2 * 3)
        new_y = 3 + (2 * 3)
        self.pointer.set_position.assert_called_with((new_x, new_y))

    def test_move_with_non_integer_multiplier(self):
        self.pointer.set_move_multiplier(3.2)
        self.pointer.get_position = mock.Mock(return_value=(2, 3))
        self.pointer.set_position = mock.Mock()
        self.pointer.move((2, 2))
        new_x = int(round(2 + (2 * 3.2)))
        new_y = int(round(3 + (2 * 3.2)))
        self.pointer.set_position.assert_called_with((new_x, new_y))

    def test_move_with_non_integer_raises_exception(self):
        self.pointer.set_move_multiplier(3)
        self.pointer.get_position = mock.Mock(return_value=(2, 3))
        self.pointer.set_position = mock.Mock()
        with self.assertRaises(Exception):
            self.pointer.move((2.0, 2.0))


if __name__ == '__main__':
    unittest.main()
