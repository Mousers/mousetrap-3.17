from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
'''
All things GUI.
'''


import logging
LOGGER = logging.getLogger(__name__)


# gtk can be patch with a Mock during testing without ever importing Gtk
# from gi.repository. This is necessary since importing Gtk from gi.repository
# on a headless system raises an error.
gtk = None


def get_gtk():
    global gtk

    if gtk is None:
        from gi.repository import Gtk
        gtk = Gtk

    return gtk

# gdk can be patch with a Mock during testing without ever importing Gdk
# from gi.repository. This is necessary since importing Gdk from gi.repository
# on a headless system raises an error.
gdk = None


def get_gdk():
    global gdk

    if gdk is None:
        from gi.repository import Gdk
        gdk = Gdk

    return gdk


from Xlib.display import Display as XlibDisplay
from Xlib.ext import xtest
from Xlib import X


from mousetrap.i18n import _


class ImageWindow(object):

    def __init__(self, config, message):
        self._config = config
        self._window = get_gtk().Window(title=message)
        self._canvas = get_gtk().Image()
        self._window.add(self._canvas)
        self._window.connect("delete-event", get_gtk().main_quit)
        self._window.show_all()

    def draw(self, image):
        '''Draw image to this window.
        '''
        image = image.to_pixbuf()
        self._canvas.set_from_pixbuf(image)
        self._canvas.queue_draw()


class Gui(object):
    _running = False

    @classmethod
    def start(cls):
        '''Start handling events.'''
        if not cls._running:
            cls._running = True
            get_gtk().main()

    @classmethod
    def stop(cls):
        '''Stop handling events.'''
        if cls._running:
            cls._running = False
            get_gtk().main_quit()

    def __init__(self, config):
        self._config = config
        self._windows = {}

    def show_image(self, window_name, image):
        '''Displays image in window named by window_name.
           May reuse named windows.
           '''
        if window_name not in self._windows:
            self._windows[window_name] = ImageWindow(self._config, window_name)
        self._windows[window_name].draw(image)

    def get_screen_width(self):
        return get_gtk().Window().get_screen().get_width()

    def get_screen_height(self):
        return get_gtk().Window().get_screen().get_height()


class Pointer(object):
    BUTTON_LEFT = X.Button1

    def __init__(self, config):
        self._config = config
        gdk_display = get_gdk().Display.get_default()
        device_manager = gdk_display.get_device_manager()
        self._pointer = device_manager.get_client_pointer()
        self._screen = gdk_display.get_default_screen()
        self._moved = False
        self._move_multiplier = self._config[self]['move_multiplier']

    def move(self, delta):
        '''Move pointer by (dx, dy) where dx and dy are defined as follows:
            dx = int(round(delta[0] * move_multiplier))
            dy = int(round(delta[1] * move_multiplier))

        move_multiplier may be set in ~/.mousetrap.yaml or by calling
        set_move_multiplier().
        '''
        (dx, dy) = delta

        if not isinstance(dx, int) or not isinstance(dy, int):
            raise Exception(_('delta elements must be integer.'))

        (x, y) = self.get_position()
        x += int(round(dx * self._move_multiplier, 0))
        y += int(round(dy * self._move_multiplier, 0))
        self.set_position((x, y))

    def set_move_multiplier(self, multiplier):
        self._move_multiplier = multiplier

    def get_position(self):
        x_index = 1
        y_index = 2
        position = self._pointer.get_position()
        return (position[x_index], position[y_index])

    def set_position(self, position=None):
        '''Move pointer to position (x, y). If position is None,
        no change is made.'''
        self._moved = False
        if position is not None:
            LOGGER.debug(_('Moving pointer to %s'), position)

            self._pointer.warp(self._screen, position[0], position[1])
            self._moved = True
        else:
            LOGGER.debug(_('Not moving the pointer'))

    def is_moving(self):
        '''Returns True if last call to set_position passed a non-None value
        for position.'''
        return self._moved

    def click(self, button=BUTTON_LEFT):
        display = XlibDisplay()
        for event, button in \
                [(X.ButtonPress, button), (X.ButtonRelease, button)]:
            LOGGER.debug('%s %s', event, button)
            xtest.fake_input(display, event, button)
            display.sync()
