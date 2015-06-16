from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
import logging
LOGGER = logging.getLogger(__name__)

from gi.repository import GLib

from mousetrap.i18n import _
from mousetrap.gui import Gui, Pointer
from mousetrap.vision import Camera


class App(object):

    def __init__(self, config):
        LOGGER.info("Initializing")
        self.config = config
        self.image = None
        self.loop = Loop(config, self)
        self.gui = Gui(config)
        self.camera = Camera(config)
        self.pointer = Pointer(config)
        self.plugins = []
        self._assemble_plugins()

    def _assemble_plugins(self):
        self._load_plugins()
        self._register_plugins_with_loop()

    def _load_plugins(self):
        for class_ in self.config['assembly']:
            self.plugins.append(self._load_plugin(class_))

    def _load_plugin(self, class_string):
        try:
            LOGGER.info('loading %s', class_string)

            class_path = class_string.split('.')
            module = __import__(
                '.'.join(class_path[:-1]), {}, {}, class_path[-1]
            )

            return getattr(module, class_path[-1])(self.config)
        except ImportError:
            LOGGER.error(
                _(
                    'Could not import plugin `%s`. ' +
                    'Check config file and PYTHONPATH.'
                ),
                class_string
            )

            raise

    def _register_plugins_with_loop(self):
        for plugin in self.plugins:
            self.loop.subscribe(plugin)

    def run(self):
        self.loop.start()
        self.gui.start()

    def stop(self):
        self.gui.stop()
        self.loop.stop()


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

    def __init__(self, config, app):
        super(Loop, self).__init__()
        self._config = config
        self._interval = None
        self._loops_per_second = None
        self._timeout_id = None
        self._set_loops_per_second(config['loops_per_second'])
        self._add_argument('app', app)
        self._loop_enabled = False

    def _set_loops_per_second(self, loops_per_second):
        self._loops_per_second = loops_per_second
        self._interval = int(round(
            self.MILLISECONDS_PER_SECOND / self._loops_per_second))

    def start(self):
        self._loop_enabled = True
        self._timeout_id = GLib.timeout_add(self._interval, self._run)

    def stop(self):
        self._loop_enabled = False

    def _run(self):
        self._fire(self.CALLBACK_RUN)
        return self._loop_enabled
