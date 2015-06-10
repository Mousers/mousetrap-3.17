from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from .engine import Engine
from .helpers import _


def parse_the_command_line_arguments():
    from argparse import ArgumentParser
    mousetrap_command = ArgumentParser()
    message=_('Loads configuration from FILE.')
    parser.add_argument('--config', metavar='FILE', help=message)
    return parser.parse_args()


def register_for_systemd_signals(engine):
    from signal import signal
    signal(signal.SIGHUP, engine.restart)
    signal(signal.SIGTERM, engine.stop)
    signal(signal.SIGINT, engine.stop)


args = parse_the_command_line_arguments()
engine = Engine(config_path=args.config)
register_for_systemd_signals(engine)
engine.start()
