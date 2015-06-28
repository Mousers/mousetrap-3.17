import mousetrap.plugins.interface as interface
import logging
import cv2
import math


LOGGER = logging.getLogger(__name__)


class Bright(interface.Plugin):
	
	
    def __init__(self, config):
        self._config = config
        self._point_buffer = PointBuffer(14)
        
        self.width_screen = None
        self.height_screen = None
        
        self.width_image = None
        self.height_image = None
        
        self.height_scale = None
        self.width_scale = None


    def run(self, app):
        if self.width_screen == None:
            self.width_screen = app.gui.get_screen_width()
            self.height_screen = app.gui.get_screen_height()
            self.height_image, self.width_image = app.image.to_cv().shape[:2]
            self.height_scale = self.height_screen / self.height_image
            self.width_scale = self.width_screen / self.width_image
            
        gray = app.image.to_cv_grayscale()
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
        newPoint = Point(math.floor(self.width_screen - (self.width_scale * maxLoc[0])), math.floor(self.height_scale * maxLoc[1]))
        self._point_buffer.addPoint(newPoint)
        average = self._point_buffer.average()
        app.pointer.set_position((average.x, average.y))
        app.pointer.get_position() #updates pointer





class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

class PointBuffer:

    def __init__(self, size):
        if size < 1:
            raise Exception("Size can't be less than 1")
        
        self.size = size
        self.points = []
        self.numElements = 0

    def getSize(self):
        return self.numElements

    def addPoint(self, pointP):
        if (self.numElements == self.size):
            self.points.pop(0)
            self.points.append(pointP)
        else:
            self.points.append(pointP)
            self.numElements += 1

    def average(self):
        averageX = 0
        averageY = 0
        
        for point in self.points:
            averageX += point.x
            averageY += point.y

        averageX //= self.numElements
        averageY //= self.numElements

        return Point(averageX, averageY)
    

    def printBuffer(self):
        outputstring = '['
        for point in self.points:
            if point != None:
                outputstring += '(' + str(point.x) + ', ' + str(point.y) + '),'

        if len(outputstring) > 1:   #Better output formatting; removes extra ','
            outputstring = outputstring[:-1]
            
        outputstring += ']'
        print(outputstring)

