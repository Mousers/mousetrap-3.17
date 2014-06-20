'''
Where it all begins.
'''

import mousetrap.log as log
from gi.repository import GObject, Gdk, Gtk
from mousetrap.gui import Gui, Pointer
from mousetrap.vision import Camera


LOGGER = log.getLogger('mousetrap.main')


#TODO: Should be a configuration file.
DEFAULT_PARTS = [
        ('camera', 'mousetrap.plugins.camera.CameraPlugin'),
        ('display', 'mousetrap.plugins.display.DisplayPlugin'),
        ('nose_joystick', 'mousetrap.plugins.nose_joystick.NoseJoystickPlugin'),
        ('eye_click', 'mousetrap.plugins.eyes.EyesPlugin'),
        ]
DEFAULT_LOOPS_PER_SECOND = 10


class App(object):
    def __init__(self):
        self.image = None
        self.loop = Loop(self)
        self.gui = Gui()
        self.camera = Camera()
        self.pointer = Pointer()
        self.plugins = []
        self._assemble_plugins()

    def _assemble_plugins(self):
        self._load_plugins(DEFAULT_PARTS)
        self._register_plugins_with_loop()

    def _load_plugins(self, plugin_descriptors):
        for name, class_ in plugin_descriptors:
            self.plugins.append(self._load_plugin(class_))

    @staticmethod
    def _load_plugin(class_):
        LOGGER.debug('loading %s', class_)
        class_path = class_.split('.')
        module = __import__('.'.join(class_path[:-1]), {}, {}, class_path[-1])
        return getattr(module, class_path[-1])()

    def _register_plugins_with_loop(self):
        for plugin in self.plugins:
            self.loop.subscribe(plugin)

    def run(self, app=None):
        self.loop.start()
        self.gui.start()


class Observable(object):
    def __init__(self):
        self.__observers = []
        self.__arguments = {}

    def subscribe(self, observer):
        self.__observers.append(observer)

    def _add_argument(self, key, value):
        self.__arguments[key] = value

    def _fire(self, callback_name):
        for observer in self.__observers:
            callback = getattr(observer, callback_name)
            callback(**self.__arguments)


class Loop(Observable):
    MILLISECONDS_PER_SECOND = 1000.0
    CALLBACK_RUN = 'run'

    def __init__(self, app):
        super(Loop, self).__init__()
        self.set_loops_per_second(DEFAULT_LOOPS_PER_SECOND)
        self._timeout_id = None
        self._add_argument('app', app)

    def set_loops_per_second(self, loops_per_second):
        self._loops_per_second = loops_per_second
        self._interval = int(round(
            self.MILLISECONDS_PER_SECOND / self._loops_per_second))

    def start(self):
        self.timeout_id = GObject.timeout_add(self._interval, self.run)

    def run(self):
        CONTINUE = True
        PAUSE = False
        self._fire(self.CALLBACK_RUN)
        return CONTINUE


if __name__ == '__main__':
    App().run()
