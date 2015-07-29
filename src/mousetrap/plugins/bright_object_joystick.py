import mousetrap.plugins.interface as interface
import logging
import cv2
import math


LOGGER = logging.getLogger(__name__)


class Bright(interface.Plugin):
    
    
    def __init__(self, config):
        self._config = config
        self._point_buffer = PointBuffer(14)
        self.DEAD_ZONE = 50
        
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
            
        print('%4.1f, %4.1f' % (delta_x, delta_y))
        pointer_location = (pointer_location[0] + delta_x, pointer_location[1] + delta_y)
        app.pointer.set_position(pointer_location)
        app.pointer.get_position()
            #print("DANGER ZONE!  " + str(maxLoc[0]))
        #else:
            
            #print(str(self.width_image//2 - 50) + ", " + str(self.width_image//2 + 50) + "  " + str(maxLoc[0]))
        
        #gray = app.image.to_cv_grayscale()
        #(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
        #newPoint = Point(math.floor(self.width_screen - (self.width_scale * maxLoc[0])), math.floor(self.height_scale * maxLoc[1]))
        #self._point_buffer.addPoint(newPoint)
        #average = self._point_buffer.average()
        #app.pointer.set_position((average.x, average.y))
        #app.pointer.get_position() #updates pointer





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
