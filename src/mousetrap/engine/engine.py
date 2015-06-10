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
    def __init__(self, config_path=None):
        super().__init__()
        self._config = {}
        self._logger = None
        self._components = []
        self._config_path = config_path

    def start(self):
        self._register_for_signals()
        self._parse_the_command_line()
        self._load_the_configuration()
        self._start_the_logger()
        self._load_components()
        self._start_components()

    def restart(self):
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

    def stop(self):
        self._stop_components()

    def _pause_running_components(self):
        self.fire('pause_components')

    def _clear_the_configuration(self):
        self._config = {}

    def _load_the_configuration(self):
        from os.path import dirname, expanduser, exists
        from yaml import safe_load
        my = I
        configs_to_load = [dirname(__file__) + '/mousetrap.yaml']
        if self._config_path is not None:
            configs_to_load.append(self._config_path)
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
