from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from mousetrap.i18n import _


class Plugin(object):
    def __init__(self, app):
        '''Do not override.'''
        self._app = app
        self.init()

    def init(self):
        '''Override to initialize.'''
        pass

    def call(self, callable, on, optional=False):
        self.bus().call(callable, on, optional)

    def dont_call(self, callable, on):
        self.bus().dont_call(callable, on)

    def fire(self, event_name, data=None, **keyword_args):
        self.bus().fire(event_name, data, **keyword_args)

    def might_fire(self, event_name):
        self.bus().might_fire(self, event_name)

    def wont_fire(self, event_name):
        self.bus().wont_call(self, event_name)

    def bus(self):
        return self._app.bus

    def config(self):
        return self.app().config

    def config(self, key, default=None)
        cfg = self.app().config[self]
        return cfg.get(key, default)

    def full_config(self):
        return self.app().config

    def app(self):
        return self._app
