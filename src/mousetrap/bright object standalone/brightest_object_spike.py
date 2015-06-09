#conversion for Adam Devigili's Processsing iControl code.
import cv2
from Xlib.display import Display as XlibDisplay
from Xlib.ext import xtest
from Xlib import X

capture = None
image = None
points = None
pointer = None



def setup():
	global capture
	global image
	global points
	global pointer

	capture = cv2.VideoCapture(0)
	points = PointBuffer(14)
	pointer = Pointer()
	pointer.set_position(position=(get_screen_width()/2, get_screen_height()/2))
	
	
    
	location = pointer.get_position()

	points.addPoint(Point(location[0], location[1]))

	draw()
	

def draw(): 
	global capture
	global image
	global points
	global pointer

	displayWidth, height = getScreenSize()

	flag = 1
	while (flag == 1):

		#scale(2) do we need this?

		image = captureEvent()		
		#cv2.loadImage(image)

		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		
		(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
		

		#clickCooldown = clickCooldown+1

		#loc = opencv.max()
		
		#print(2*maxLoc[0])
		
		
		newPoint = Point(displayWidth - abs(int(2*maxLoc[0])), int(2*maxLoc[1]))
			#dependent on how the new Point class is written
		
		points.addPoint(newPoint)    #dependent on how the new PointBuffer class is written

		nextMove = points.average()         #dependent on how the new PointBuffer class is written

		pointer.set_position((nextMove.x, nextMove.y))
		#calling this function is the only way i could find to update the pointer
		pointer.get_position()
		

def get_screen_width():
    return get_gtk().Window().get_screen().get_width()

def get_screen_height():
    return get_gtk().Window().get_screen().get_height()

# gtk can be patch with a Mock during testing without ever importing Gtk
# from gi.repository. This is necessary since importing Gtk from gi.repository
# on a headless system raises an error.
gtk = None


def get_gtk():
    global gtk

    if gtk is None:
        from gi.repository import Gtk
        gtk = Gtk

    return gtk

# gdk can be patch with a Mock during testing without ever importing Gdk
# from gi.repository. This is necessary since importing Gdk from gi.repository
# on a headless system raises an error.
gdk = None


def get_gdk():
    global gdk

    if gdk is None:
        from gi.repository import Gdk
        gdk = Gdk

    return gdk

def getScreenSize():
	window = get_gtk().Window()
	screen = window.get_screen()
	return (screen.get_width(), screen.get_height())

class Pointer(object):
    BUTTON_LEFT = X.Button1

    def __init__(self):
        gdk_display = get_gdk().Display.get_default()
        device_manager = gdk_display.get_device_manager()
        self._pointer = device_manager.get_client_pointer()
        self._screen = gdk_display.get_default_screen()
        self._moved = False

    def set_position(self, position=None):
        '''Move pointer to position (x, y). If position is None,
        no change is made.'''
        self._moved = False
        if position is not None:
        	#print(position[0], position[1])
        	self._pointer.warp(self._screen, position[0], position[1])
        	self._moved = True

    def is_moving(self):
        '''Returns True if last call to set_position passed a non-None value
        for position.'''
        return self._moved

    def get_position(self):
        x_index = 1
        y_index = 2
        position = self._pointer.get_position()
        return (position[x_index], position[y_index])

    def click(self, button=BUTTON_LEFT):
        display = XlibDisplay()
        for event, button in \
                [(X.ButtonPress, button), (X.ButtonRelease, button)]:
            xtest.fake_input(display, event, button)
            display.sync()

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

def captureEvent():
	global capture
	ret, image = capture.read()
	return image
	



####################  TESTS  ####################

def main():
    pb = PointBuffer(5)
    print(pb.getSize()) # should print: 0
    pb.printBuffer()    # should print: []
    pb.addPoint(Point(100, 100))
    pb.addPoint(Point(50, 150))
    print(pb.getSize()) # should print: 2
    pb.addPoint(Point(200, 50))
    pb.addPoint(Point(300, 300))
    pb.addPoint(Point(0, 50))
    pb.printBuffer()    # should print: [(100, 100),(50, 150),(200, 50),(300, 300),(0, 50)]
    pb.addPoint(Point(250, 200))
    pb.printBuffer()    # should print: [(50, 150),(200, 50),(300, 300),(0, 50),(250, 200)]
    print(pb.getSize()) # should print: 5

    average = pb.average()
    print('average is (' + str(average.x) + ', ' + str(average.y) + ')')
	
	# should print: average is (160, 150)

    #image = captureEvent()
    #cv2.imwrite("test.png", image)


    setup()
	

main()



# minor test for finding brightest object point

#capture = cv2.VideoCapture(0)
#image = captureEvent()
#cv2.imwrite("test.png", image)
#orig = image.copy()
#gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
#cv2.circle(image, maxLoc, 5, (255, 0, 0), 2)
#cv2.imwrite("test2.png", image)
