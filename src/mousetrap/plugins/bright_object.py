import mousetrap.plugins.interface as interface
import logging


LOGGER = logging.getLogger(__name__)


class Bright(interface.Plugin):
	
	
    def __init__(self, config):
        self._config = config
        self.width = None
        self.height = None
        self._point_buffer = PointBuffer(14)


    def run(self, app):
        if self.width == None:
            self.width = app.gui.get_screen_width()
            self.height = app.gui.get_screen_height()
        gray = cv2.cvtColor(app.image, cv2.COLOR_BGR2GRAY)
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
        newPoint = Point(displayWidth - abs(int(2*maxLoc[0])), int(2*maxLoc[1]))
        self._point_buffer.addPoint(newPoint)
        average = points.average()
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

