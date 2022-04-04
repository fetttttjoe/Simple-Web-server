# TODO: implement a way so i can have more than one screen in a frame or something
#       monitor detection etc already implemented 
#  -> Sometimes there are weird EOF errors. I think they come from the yield
#     -> eighter check if empty OR somehow find the way to do it properly 
# https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited
# https://blog.miguelgrinberg.com/post/video-streaming-with-flask
# 
import cv2 as cv # https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
from mss import mss # https://python-mss.readthedocs.io/examples.html1
import numpy as np
from threading import Thread, RLock
import time
import logging
logger = logging.getLogger(__name__)

class Stream(object):
    # Class variables for each thread 
    cMAXSTREAMS = 5 # fixed for now
    cSTREAMCOUNT = 0 
    # Put them into one array at some point 
    cMONITORS = np.full((cMAXSTREAMS), None)
    cSTREAMS = np.full((cMAXSTREAMS), None)
    cLASTACCESS = np.full((cMAXSTREAMS), None)
    cFRAMES = np.full((cMAXSTREAMS), None) # alot of io requests i guess, i should find a better solution
    __lock = RLock()
    #
    # Constructor i am sure this is not the best solution 
    # the amount of objects and _ThreadCount are kinda the same
    # TODO: learn about pools and redo this class
    #   
    #
    def __init__(self, monitor):
        if monitor in Stream.cMONITORS: # we dont need to monitor the same exact same area twise 
            raise ValueError('Stream already created')
        while Stream.cSTREAMCOUNT >= Stream.cMAXSTREAMS: # make sure we have some kind of limit 
            print(f"Max Objects reached! Only {Stream.cMAXSTREAMS} allowed") # DEBUG
            for num, element in enumerate(Stream.cSTREAMS): # find a place for the new stream 
                print(num, element)
                if element is None:
                    self.id = num
                    break
        self.id = Stream.cSTREAMCOUNT
        Stream.cSTREAMCOUNT += 1
        Stream.cMONITORS[self.id] = monitor
        self.monitor = monitor
        print(f"__init__ Object with ID[{self.id}] created. Monitoring: {monitor}")
        logging.debug(f"__init__ for ID: {self.id} {Stream.cSTREAMS} {Stream.cSTREAMS[self.id]}")
    #
    # Should be called on object destruction, but i am not sure if i understood correctlys
    #
    def __exit__(self):
        print(f"exiting object {self}")
        Stream.cMONITORS[self.id] = None
    #
    # Getter for maxStreams
    #
    @staticmethod
    def getMaxStreams():
        return Stream.cMAXSTREAMS
    #    
    # Getter for current frame
    #
    def getCurrentFrame(self):
        logging.debug(f"getCurrentFrame self: {self}")
        logging.debug(f"getCurrentFrame[{self.id}] time: {Stream.cLASTACCESS[self.id]}, {type(Stream.cFRAMES[self.id])}")
        #for num, element in enumerate(Stream.cFRAMES):                  # DEBUG
        #    print(f"get Current Frame with type:{type(element)} at Pos:({num})")    # DEBUG
        with Stream.__lock:
            Stream.cLASTACCESS[self.id] = time.time() # update the time Stamp with latest Request time
            return Stream.cFRAMES[self.id] # Return the frame from Thread
    #
    # Start the Stream from Outside
    #
    def startStream(self):
        if Stream.cSTREAMS[self.id] is None:
            Stream.cMONITORS[self.id] = Stream.cMONITORS[self.id]
            logging.debug(f"startStream object Created for: {Stream.cMONITORS[self.id]}") # DEBUG
            Stream.cLASTACCESS[self.id] = time.time()
            Stream.cSTREAMS[self.id] = Thread(target=self._thread)
            logging.debug(f"startStream Thread{self.id} created {self.cSTREAMS[self.id]}") # DEBUG
            logging.debug(self.cSTREAMS) #DEBUG
            Stream.cSTREAMS[self.id].daemon = True
            Stream.cSTREAMS[self.id].start()
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
            logging.debug(f"frameStream from Thread[{self.id}] for Monitor: {Stream.cMONITORS[self.id]}") #DEBUG
            raw = sct.grab(Stream.cMONITORS[self.id]) #grab data from screen using mss
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
        logging.debug(f"Thread at: {self.cSTREAMS[self.id]}") # DEBUG
        while True:
            frame = self.generateFrame() #get the frame 
            with Stream.__lock: # make sure we lock ressource from access 
                Stream.cFRAMES[self.id] = frame # add the frame to class attrib cFRAMES   
                time.sleep(.5)
            if time.time() - Stream.cLASTACCESS[self.id] > waitTimeOut: # if there is no user interaction for waitTimeOut end thread
                logging.debug(f'No User conntection for {waitTimeOut} seconds Thread[{self.id}] will be closed')
                break
        # make sure thread gets unloaded
        print(Stream.cSTREAMCOUNT) # DEBUG
        with Stream.__lock:
            Stream.cSTREAMS[self.id] = None           #TODO: I can imagine a few cases where this section is going to fail redo this with class     
            Stream.cFRAMES[self.id] = None
            Stream.cSTREAMCOUNT -= 1; #   -> Check this and keep an eye on that
        logging.debug(f"_thread: Stream.cSTREAMCOUNT: {Stream.cSTREAMCOUNT} Stream.cSTREAMS: {Stream.cSTREAMS}") # DEBUG