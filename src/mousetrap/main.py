from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

'''
Where it all begins.
'''

from argparse import ArgumentParser
from io import open
import logging
import logging.config
from os.path import dirname, expanduser, exists
import signal
import sys
import yaml

from mousetrap.config import Config
from mousetrap.core import App


class Main(object):
    DEFAULT_CONFIG_PATH = dirname(__file__) + '/mousetrap.yaml'
    USER_CONFIG_PATH = expanduser('~/.mousetrap.yaml')

    def __init__(self):
        try:
            self._app = None
            self._args = CommandLineArguments()
            self._handle_dump_annotated()
            self._config = Config().load(self._get_config_paths())
            self._handle_dump_config()
            self._configure_logging()
        except ExitException:
            sys.exit(0)

    def _get_config_paths(self):
        paths = [self.DEFAULT_CONFIG_PATH]
        if exists(self.USER_CONFIG_PATH):
            paths.append(self.USER_CONFIG_PATH)
        if self._args.config is not None:
            paths.append(self._args.config)
        return paths

    def _handle_dump_annotated(self):
        if self._args.dump_annotated:
            self._dump_annotated()
            raise ExitException()

    def _handle_dump_config(self):
        if self._args.dump_config:
            self._dump_config()
            raise ExitException()

    @classmethod
    def _dump_annotated(cls):
        with open(cls.DEFAULT_CONFIG_PATH, 'r') as annotated_file:
            print(annotated_file.read())

    def _dump_config(self):
        print(yaml.dump(dict(self._config), default_flow_style=False))

    def _configure_logging(self):
        logging.config.dictConfig(self._config['logging'])
        logger = logging.getLogger('mousetrap.main')
        logger.debug(yaml.dump(dict(self._config), default_flow_style=False))

    def run(self):
        self._app = App(self._config)
        signal.signal(signal.SIGTERM, self._stop_signal_handler)
        signal.signal(signal.SIGINT, self._stop_signal_handler)
        self._app.run()

    def _stop_signal_handler(self, signal_number, stack_frame):
        self._app.stop()


class CommandLineArguments(object):
    def __init__(self):
        parser = ArgumentParser()
        parser.add_argument(
            "--config",
            metavar="FILE",
            help="Loads configuration from FILE."
        )
        parser.add_argument(
            "--dump-config",
            help="Loads and dumps current configuration to standard out.",
            action="store_true"
        )
        parser.add_argument(
            "--dump-annotated",
            help=(
                "Dumps default configuration (with comments) to standard out."
            ),
            action="store_true"
        )
        parser.parse_args(namespace=self)


class ExitException(Exception):
    pass


def main():
    Main().run()


if __name__ == '__main__':
    main()
