from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from logging
from logging.config


class Log(object):
    def __init__(self):
        pass

    def close(self):
        logging.shutdown()
        reload(logging)

    def open(self, config={}):
        logging.config.dictConfig(config)

    def get_logger(self, obj):
        '''Return logger for obj.'''
        return logging.getLogger(obj.__class__.__module__)
