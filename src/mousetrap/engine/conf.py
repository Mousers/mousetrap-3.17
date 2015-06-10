from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from ..helpers import update_dict_recursively


class Conf(object):
    def __init__(self, config_path=None):
        self._config_path = config_path
        self._conf = {}

    def load(self):
        from os.path import dirname, expanduser, exists
        from yaml import safe_load
        configs_to_load = [dirname(__file__) + '/../mousetrap.yaml']
        if self._config_path is not None:
            configs_to_load.append(self._config_path)
        else:
            configs_to_load.append(expanduser('~/.mousetrap.yaml'))
        configs_to_load = [f for f in configs_to_load if exists(f)]
        for config_path in configs_to_load:
            with open(config_path) as config_file:
                config = safe_load(config_file)
            update_dict_recursively(self._conf, config)

    def clear(self):
        self._conf = {}

    def dict(self, context=None):
        if context is not None:
            class_ = context.__class__
            fqname = class_.__module__ + '.' + class_.__name__
            return self._conf['classes'][fqname]
        else:
            return self._conf
