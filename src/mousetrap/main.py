from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from os.path import dirname
from os.path import expanduser

from .lib import _
from .lib import conf
from .lib import logger
from .lib import Engine


class Main(object):
    def __init__(self):
        self._args = None
        self._conf_default = dirname(__file__) + '/config.yaml'
        self._conf_user = expanduser('~/.mousetrap.yaml')
        self._engine = Engine()
        self._register_for_systemd_signals()

    def _register_for_systemd_signals(self):
        from signal import signal, SIGHUP, SIGTERM, SIGINT
        signal(SIGHUP, self.restart)
        signal(SIGTERM, self.stop)
        signal(SIGINT, self.stop)

    def start(self):
        conf.load(self._conf_default)
        logger.configure(conf['logging'])
        self._args = self._parse_the_command_line_arguments()
        conf.load(first_of=[self._args.config, self._conf_user])
        logger.shutdown()
        logger.configure(conf['logging'])
        self._engine.start()

    def restart(self, *args, **kwargs):
        self._engine.pause()
        conf.clear()
        conf.load(self._conf_default)
        conf.load(first_of=[self._args.config, self._conf_user])
        logger.shutdown()
        logger.configure(conf['logging'])
        self._engine.resume()

    def stop(self, *args, **kwargs):
        self._engine.stop()
        logger.shutdown()

    def _parse_the_command_line_arguments(self):
        from argparse import ArgumentParser
        mousetrap_command = ArgumentParser()
        message=_('Loads configuration from FILE.')
        mousetrap_command.add_argument('--config', metavar='FILE', help=message)
        return mousetrap_command.parse_args()


main = Main()
main.start()
