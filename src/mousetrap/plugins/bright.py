import mousetrap.plugins.interface as interface
import logging
import cv2
import math


LOGGER = logging.getLogger(__name__)


class Bright(interface.Plugin):
    
    
    def __init__(self, config):
        self._config = config
        self.DEAD_ZONE = config[self]['dead_zone']
             
        self.width_image = None
        self.height_image = None
           

    def run(self, app):
        if self.height_image == None:
            
            self.height_image, self.width_image = app.image.to_cv().shape[:2]
            
        pointer_location = app.pointer.get_position()
        gray = app.image.to_cv_grayscale()
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
        delta_x = 0
        delta_y = 0
        if not ((self.width_image//2 + self.DEAD_ZONE) > maxLoc[0] > (self.width_image//2 - self.DEAD_ZONE)):
            if maxLoc[0] < self.width_image//2:
                delta_x = (self.width_image//2 - self.DEAD_ZONE - maxLoc[0]) * 0.1
            else:
                delta_x = (maxLoc[0] - (self.width_image//2 + self.DEAD_ZONE)) * -0.1
            
        if not ((self.height_image//2 + self.DEAD_ZONE) > maxLoc[1] > (self.height_image//2 - self.DEAD_ZONE)):
            if maxLoc[1] < self.height_image//2:
                delta_y = (self.height_image//2 - self.DEAD_ZONE - maxLoc[1]) * -0.1
            else:
                delta_y = (maxLoc[1] - (self.height_image//2 + self.DEAD_ZONE)) * 0.1
            
        pointer_location = (pointer_location[0] + delta_x, pointer_location[1] + delta_y)
        app.pointer.set_position(pointer_location)
        app.pointer.get_position()
            


