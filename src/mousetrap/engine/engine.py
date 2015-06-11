from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import logging

from .bus import Bus
from .conf import Conf
from .log import Log


class Engine(object):
    '''Provides the core infrastructure for MouseTrap. In particular, it
    manages the components of the system, responds to POSIX signals, and
    provides an API to access the following system-wide resources:

    1. Logging
    2. Configuration
    3. Communication bus (can call Bus methods directly on Engine instance)

    Engine may fire the following events:

    - start_components -- start stopped components
    - stop_components -- stop running and paused components
    - pause_components -- pause running components
    - resume_components -- restart paused components
    '''
    def __init__(self, config_path=None):
        self._conf = Conf(config_path)
        self._log = Log()
        self._components = []
        self._bus = Bus()
        self._bus.may_fire('start_components')
        self._bus.may_fire('stop_components')
        self._bus.may_fire('pause_components')
        self._bus.may_fire('resume_components')

    def __getattr__(self, name):
        '''Dispatches unfound members to _bus.'''
        try:
            return getattr(self._bus, name)
        except AttributeError as error:
            raise AttributeError("'Engine' object has no attribute '%s'" %
                    (name))

    def start(self):
        self._load_configuration()
        self._open_log()
        self._load_components()
        self._start_components()

    def restart(self):
        self._pause_running_components()
        self._clear_configuration()
        self._load_configuration()
        self._close_log()
        self._open_log()
        self._stop_disabled_components()
        self._unload_disabled_components()
        self._load_enabled_components()
        self._resume_components()
        self._start_components()

    def stop(self):
        self._stop_components()
        self._close_log()

    def _pause_running_components(self):
        self.fire('pause_components')

    def _clear_configuration(self):
        self._conf.clear()

    def _load_configuration(self):
        self._conf.load()

    def _open_log(self):
        self._log.open(self.conf()['logging'])

    def _close_log(self):
        self._log.close()

    def _stop_disabled_components(self):
        for component in self._disabled_components():
            component._stop()

    def _unload_disabled_components(self):
        for component in self._disabled_components():
            self._components.remove(component)

    def _disabled_components(self):
        enabled = self._enabled_components()
        return [x for x in self._components if x.__name__ not in enabled]

    def _enabled_components(self):
        '''Return list of enabled components.'''
        return self.conf()['enabled_components']

    def _load_components(self):
        self._load_enabled_components()

    def _load_enabled_components(self):
        '''Load components not already loaded.'''
        loaded = [x.__name__ for x in self._components]
        enabled = [x for x in self._enabled_components() if x not in loaded]
        for class_ in enabled:
            try:
                self.logger(self).info('loading %s', class_)
                class_path = class_.split('.')
                name = '.'.join(class_path[:-1])
                module = __import__(name, {}, {}, class_path[-1])
                component = getattr(module, class_path[-1])(self)
            except ImportError:
                msg = _('Could not import component `%s`.')
                self.logger(self).error(msg, class_string)
                raise
            self._components.append(component)

    def _start_components(self):
        self.fire('start_components')

    def _resume_components(self):
        self.fire('resume_components')

    def conf(self, context=None):
        '''Return the configuration dictionary. If context is provided, it
        returns just the part of the configuration dictionary that corresponds
        to context's class.
        '''
        return self._conf.dict(context)

    def logger(self, context):
        '''Return the logger associated with context.'''
        return self._log.get_logger(obj)
