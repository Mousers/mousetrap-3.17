from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import logging


def Log(object):
    def close(self):
        logging.shutdown()
        reload(logging)

    def open(self, config):
        import logging.config
        logging.config.dictConfig(config)

    def get_logger(self, obj):
        '''Return logger for obj.'''
        return logging.getLogger(obj.__class__.__module__)
