# TODO: implement a way so i can have more than one screen in a frame or something
#       monitor detection etc already implemented 
#  -> Sometimes there are weird EOF errors. I think they come from the yield
#     -> eighter check if empty OR somehow find the way to do it properly 
# https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited
# https://blog.miguelgrinberg.com/post/video-streaming-with-flask
# 
import threading
import cv2 as cv # https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
from mss import mss # https://python-mss.readthedocs.io/examples.html1
import numpy as np
from threading import Thread, RLock
import time
import itertools
import logging
logger = logging.getLogger(__name__)

class Stream(object):
    # Class variables for each thread 
    maxStreams = 5 # fixed for now
    streamCount = 0 
    classMonitor = np.full((maxStreams), None)
    classStreams = np.full((maxStreams), None)
    classFrames = np.full((maxStreams), None)
    classLastAccess = np.full((maxStreams), None)
    __lock = RLock()
    #
    # Constructor i am sure this is not the best solution 
    # the amount of objects and _ThreadCount are kinda the same
    # TODO: learn about pools and redo this class
    #   Critical: EVERY device needs 2 threads for both windows 
    #               -> because we create objects on every call 
    #               ->    
    #
    def __init__(self, monitor):
        while Stream.streamCount >= Stream.maxStreams: # make sure we have some kind of limit 
            logging.debug(f"Max Objects reached! Only {Stream.maxStreams} allowed") # DEBUG
            for num, element in enumerate(Stream.classStreams):
                print(num, element)
                if element is None:
                    self.id = num
                    break
        if Stream.streamCount < Stream.maxStreams:
            self.id = Stream.streamCount
        print(f"__init__ Object with ID[{self.id}] created")
        Stream.streamCount += 1
        Stream.classMonitor[self.id] = monitor
        self.monitor = monitor
        #if monitor in Stream.classMonitor:
        #    raise ValueError('Stream already created')
        logging.debug(f"__init__ for ID: {self.id} {Stream.classStreams} {Stream.classStreams[self.id]}")
    #    
    # Getter for current frame
    #
    def getCurrentFrame(self):
        logging.debug(f"getCurrentFrame self: {self}")
        logging.debug(f"getCurrentFrame[{self.id}] time: {Stream.classLastAccess[self.id]}, {type(Stream.classFrames[self.id])}")
        #for num, element in enumerate(Stream.classFrames):                  # DEBUG
        #    print(f"get Current Frame with type:{type(element)} at Pos:({num})")    # DEBUG
        with Stream.__lock:
            Stream.classLastAccess[self.id] = time.time() # update the time Stamp with latest Request time
            return Stream.classFrames[self.id] # Return the frame from Thread
    #
    # Start the Stream from Outside
    #
    def startStream(self):
        if Stream.classStreams[self.id] is None:
            Stream.classMonitor[self.id] = Stream.classMonitor[self.id]
            logging.debug(f"startStream object Created for: {Stream.classMonitor[self.id]}") # DEBUG
            Stream.classLastAccess[self.id] = time.time()
            Stream.classStreams[self.id] = Thread(target=self._thread)
            logging.debug(f"startStream Thread{self.id} created {self.classStreams[self.id]}") # DEBUG
            logging.debug(self.classStreams) #DEBUG
            Stream.classStreams[self.id].daemon = True
            Stream.classStreams[self.id].start()
    #           
    #
    # grabs the given monitor area and returns the generator 
    # monitor = {'top'      : pixel-pos,
    #            'left'     : pixel-pos,                
    #            'width'    : window-width,
    #            'height'   : window-height
    #           }
    # fps = default 0.5 -> a ss every 2 sek
    #   -> if set to 0 its "unlimited"
    # scalePercent = default 30 -> how much we want to scale the img
    #       example: scalePercent=30  -> 30% of original img size
    #   
    #
    def generateFrame(self, scalePercent=30, fps:int=1):
        if fps == 0: 
            sleepTimer = 0
        else: 
            sleepTimer = (1 * (1 // fps)) # make even numbers
        with mss() as sct:
            time.sleep(sleepTimer) # we only want a screenshots with given ftps
            logging.debug(f"frameStream from Thread[{self.id}] for Monitor: {Stream.classMonitor[self.id]}") #DEBUG
            raw = sct.grab(Stream.classMonitor[self.id]) #grab data from screen using mss
            img = np.array(raw) # create numpy array
            dim = ( int(img.shape[1] * scalePercent / 100) ,    # scale the img width
                    int(img.shape[0] * scalePercent / 100))     # scale the img height
            resized = cv.resize(img, dim, interpolation = cv.INTER_AREA) # resize the img
            # encode as a jpeg image  -> https://www.geeksforgeeks.org/python-opencv-imencode-function/
            # encode image into stream data
            # convert stream data into numpy array
            # convert numpy array into bytes
            byteImg = cv.imencode('.jpg', resized)[1].tobytes() 
            return byteImg # return the byteimg 
    #
    # method for custom Thread
    #
    def _thread(self, waitTimeOut = 10):
        logging.debug(f"Starting stream thread [{self.id}]. waitTimeOut: {waitTimeOut}") # DEBUG
        logging.debug(f"Thread at: {self.classStreams[self.id]}") # DEBUG
        while True:
            frame = self.generateFrame() #get the frame 
            with Stream.__lock: # make sure we lock ressource from access 
                Stream.classFrames[self.id] = frame # add the frame to class attrib classFrames   
                time.sleep(.5)
            if time.time() - Stream.classLastAccess[self.id] > waitTimeOut: # if there is no user interaction for waitTimeOut end thread
                logging.debug(f'No User conntection for {waitTimeOut} seconds Thread[{self.id}] will be closed')
                break
        # make sure thread gets unloaded
        print(Stream.streamCount) # DEBUG
        with Stream.__lock:
            Stream.classStreams[self.id] = None           #TODO: I can imagine a few cases where this section is going to fail redo this with class     
            Stream.classFrames[self.id] = None
            Stream.streamCount -= 1; #   -> Check this and keep an eye on that
        print(Stream.streamCount, Stream.classStreams ) # DEBUG