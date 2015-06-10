from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import logging

from .bus import Bus

'''
    # Start mousetrap service.
    $ mousetrap

    # Start mousetrap using specified configuration.
    $ mousetrap --config=/path/to/config.yaml
'''


class Engine(Bus):
    '''
    Responsibilities:
        1. Respond to POSIX signals consistent with their use in systemd.
            1.a start
            1.b stop
            1.c reload - reload the configuration and logs
        2. Manage the life cycle of components.
        3. Provide an API for Component. This API is not initially exposed to
            Subclasses of Component, and subclasses should not use this API
            directly. Instead subclasses of Component should only use the API
            exposed by Component.

    Protected members (those starting with _) are not part of the interface
    exposed to Component.
    '''
    def __init__(self):
        super().__init__()
        self._arguments = None
        self._config = {}
        self._logger = None
        self._components = []

    def _start(self):
        self._register_for_signals()
        self._parse_the_command_line()
        self._load_the_configuration()
        self._start_the_logger()
        self._load_components()
        self._start_components()

    def _restart(self):
        self._pause_running_components()
        self._clear_the_configuration()
        self._load_the_configuration()
        self._stop_the_logger()
        self._start_the_logger()
        self._stop_unneeded_components()
        self._remove_unneeded_components()
        self._load_needed_components()
        self._resume_components()
        self._start_components()

    def _register_for_signals(self):
        from signal import signal
        signal(signal.SIGHUP, self._restart)
        signal(signal.SIGTERM, self._stop)
        signal(signal.SIGINT, self._stop)

    def _parse_the_command_line(self):
        from argparse import ArgumentParser
        mousetrap_command = ArgumentParser()
        message=_('Loads configuration from FILE.')
        parser.add_argument('--config', metavar='FILE', help=message)
        self._arguments = parser.parse_args()

    def _pause_running_components(self):
        self.fire('pause_components')

    def _clear_the_configuration(self):
        self._config = {}

    def _load_the_configuration(self):
        from os.path import dirname, expanduser, exists
        from yaml import safe_load
        my = I
        configs_to_load = [dirname(__file__) + '/mousetrap.yaml']
        if self._arguments.config is not None:
            configs_to_load.append(self._arguments.config)
        else:
            configs_to_load.append(expanduser('~/.mousetrap.yaml'))
        configs_to_load = [f for f in configs_to_load if exists(filename)]
        for config_path in configs_to_load:
            with open(config_path) as config_file:
                config = safe_load(config_file)
            self._recursively_update_dict(self._config, config)

    def _stop_the_logger(self):
        logging.shutdown()
        reload(logging)

    def _load_the_logger(self):
        import logging.config
        logging.config.dictConfig(self._config['logging'])
        self._logger = logging.getLogger('mousetrap.service')

    def _reload_the_logger(self):
        logging.shutdown()
        reload(logging)
        self._load_the_logger()

    def _stop_unneeded_components(self):
        for component in self._unneeded_components():
            component._stop()

    def _remove_unneeded_components(self):
        for component in self._unneeded_components():
            self._components.remove(component)

    def _unneeded_components(self):
        needed = self._config['components']
        return [x for x in self._components if x.__name__ not in needed]

    def _load_needed_components(self):
        '''Load components not already loaded.'''
        loaded = [x.__name__ for x in self._components]
        needed = [x for x in self._config['components'] if x not in loaded]
        for class_ in needed:
            try:
                self._logger.info('loading %s', class_)
                class_path = class_.split('.')
                name = '.'.join(class_path[:-1])
                module = __import__(name, {}, {}, class_path[-1])
                component = getattr(module, class_path[-1])(self)
            except ImportError:
                msg = _('Could not import component `%s`.')
                self._logger.error(msg, class_string)
                raise
            self._components.append(component)

    def _start_components(self):
        self.fire('start_components')

    def _resume_components(self):
        self.fire('resume_components')

    def _stop(self):
        self.fire('stop_components')

    def _recursively_update_dict(self, target, source):
        from copy import deepcopy
        if source is None:
            return
        for key, value in source.items():
            if isinstance(value, dict):
                target[key] = target.get(key, {})
                self._recursively_update_dict(target[key], value)
            else:
                target[key] = deepcopy(value)

    def config(self, obj=None):
        '''Return config dictionary. If an obj is given, return just the
        configuration section for that object's class.
        '''
        if obj is None:
            return self._config
        else:
            class_ = obj.__class__
            fqname = class_.__module__ + '.' + class_.__name__
            return self._config['classes'][fqname]

    def logger(self, obj):
        '''Return logger for obj.'''
        return logging.getLogger(obj.__class__.__module__)



class Component(object):
    '''Components provide units of functionality for MouseTrap. Components
    communicate with eachother through events.

    Each component is in one of three states: stopped. running. or paused. A
    component is initially in the stopped state. A component only receives or
    fires events from other components in the running state (it may still
    receive events from the system). A component in the stopped state uses
    minimal resources, whereas a component in the paused state retains
    resources in anticipation of being resumed.

    To implement a component, inherit from Component and override init(),
    start(), pause(), resume(), and stop() as needed. You may also call
    Component's on() method to register callbacks for events. These will
    automatically be registered and unregistered when your component's state is
    changed. For example when your component transitions from stopped to
    running, all callbacks that you registered using the component's on() are
    automatically registered for the events. When your component is paused,
    they will automatically be unregistered. You can also use component's off()
    to unregister callbacks for events.

    Methods starting with _ are not intended to be overriden.
    '''

    STATE_STOPPED = 0
    STATE_RUNNING = 1
    STATE_PAUSED = 2

    def __init__(self, service):
        '''Do not override. Instead override init().'''
        self._service = service
        self._state = self.STATE_STOPPED
        self._event_registrations = []
        self._service.call(self._start, on='start_components')
        self.init()

    def init(self):
        '''Initialize the component. Override this instead of __init__().
        Do not perform resource intensive initialization here.
        '''
        pass

    def _start(self, event):
        '''Start the component.
        Do not override this method unless you know what you are doing.
        Instead override start().
        '''
        self._service.dont_call(self._start, on='start_components')
        self._service.call(self._stop, on='stop_components')
        self._service.call(self._pause, on='pause_components')
        for registration in self._event_registrations:
            registration.register(bus=self._service)
        self._state = self.STATE_RUNNING
        self.start()

    def start(self):
        '''Start the component. Perform any resource intensive initialization.
        Since the configuration may have changed, also check and adjust the
        configuration.
        '''
        pass

    def _stop(self, event):
        '''Stop the component.
        Do not override this method unless you know what you are doing.
        Instead override start().
        '''
        self._service.dont_call(self._stop, on='stop_components')
        self._service.dont_call(self._pause, on='pause_components')
        self._service.call(self._start, on='start_components')
        for registration in self._event_registrations:
            registration.unregister(bus=self._service)
        self._state = self.STATE_STOPPED
        self.stop()

    def stop(self):
        '''Stop the component and free resources.'''
        pass

    def _pause(self, the_event):
        '''Event callback that pauses the component.
        Do not override this method unless you know what you are doing.
        Instead override start().
        '''
        self._service.dont_call(self._pause, on='pause_components')
        self._service.call(self._stop, on='stop_components')
        self._service.call(self._resume, on='resume_components')
        for registration in self._event_registrations:
            registration.unregister(bus=self._service)
        self._state = self.STATE_PAUSED
        self.pause()

    def pause(self):
        '''Pause the component without freeing resources.'''
        pass

    def _resume(self, the_event):
        '''Resume the component.
        Do not override this method unless you know what you are doing.
        Instead override start().
        '''
        self._service.dont_call(self._resume, on='resume_components')
        self._service.call(self._stop, on='stop_components')
        self._service.call(self._pause, on='pause_components')
        for registration in self._event_registrations:
            registration.register(bus=self._service)
        self._state = self.STATE_RUNNING
        self.resume()

    def resume(self):
        '''Start the component after having been paused. Since the
        configuration may have changed, check and adjust to the
        current configuration. Unless a change in configuration indicates
        otherwise, the component does not need to perform resource intensive
        initialization.  However, if a change in configuration warrents
        reinitialization, then the component may do so.
        '''
        pass

    def call(self, callback, on, optional=False):
        '''Register callback for event_name.'''
        registration = EventRegistration(callback, on, optional)
        self._event_registrations.append(registration)
        if self._state == self.STATE_RUNNING:
            registration.register(self._service)

    def dont_call(self, callback, on):
        '''Unregister callback for event_name.'''
        registration = EventRegistration(callback, on)
        self._event_registrations.remove(registration)
        self._service.dont_call(callback, on)

    def fire(self, event_name, **data):
        '''Fire event_name with keyword parameters as data.'''
        self._service.fire(event_name, data, source=self)

    def may_fire(self, event_name):
        self._service.may_fire(self, event_name)

    def wont_fire(self, event_name):
        self._service.wont_fire(self, event_name)

    def logger(self):
        return self._service.logger(self)

    def config(self):
        return self._service.config(self)

    def config_full(self):
        return self._service.config()


class EventRegistration(object):
    '''Represents a callback being registered for an event.'''
    def __init__(self, callback, event_name, optional=False, trace=None):
        import traceback
        self.trace = trace if trace is not None else traceback.extract_stack()
        self.event_name = event_name
        self.callback = callback
        self.optional = optional
        self.trace = trace

    def register(self, bus):
        bus.call(self.callback, self.event_name, self.optional, self.trace)

    def unregister(self, bus):
        bus.dont_call(self.callback, on=self.event_name)

    def __eq__(self, other):
        return self.event_name == other.event_name and \
                self.callback == other.callback

#####################################################################
#                                                                   #
#  STRING -- Base type of strings in Python 2 or 3. Use with        #
#  isinstance to check if a value is a string type. E.g.,           #
#  isinstance(x, STRING)                                            #
#                                                                   #
#####################################################################

def _get_string_type():
    import sys
    PYTHON_3 = sys.version_info[0] == 3
    return (str, ) if PYTHON_3 else (basestring, )

STRING = _get_string_type()

#####################################################################
#                                                                   #
#  _(str) -- _ is shorthand for translations.gettext. Use it to     #
#  get mark that a string should be translated, and return the      #
#  translated string. E.g., _('This will be translated.').          #
#                                                                   #
#####################################################################

def _get_translation_function():
    import gettext
    from os.path import abspath, dirname, join, realpath
    locale_dir = abspath(join(dirname(realpath(__file__)), "locale"))
    translations = gettext.translation("mousetrap", localedir=locale_dir)
    try:
        return translations.ugettext
    except AttributeError:
        return translations.gettext

_ = _get_translation_function()

#####################################################################
#                                                                   #
#  Start the MouseTrap service if this module is ran from the       #
#  command line.                                                    #
#                                                                   #
#####################################################################

if __name__ == '__main__':
    service = Service()
    service._start()
