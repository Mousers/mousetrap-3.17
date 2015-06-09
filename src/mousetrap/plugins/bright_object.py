import mousetrap.plugins.interface as interface
import logging


LOGGER = logging.getLogger(__name__)


class Bright(interface.Plugin):
	
	
	def __init__(self, config):
	    self._config = config
	    
	
	def run(self, app):
	    
