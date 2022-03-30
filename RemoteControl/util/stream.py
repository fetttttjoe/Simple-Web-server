# TODO: implement a way so i can have more than one screen in a frame or something
#       monitor detection etc already implemented 
#  -> Sometimes there are weird EOF errors. I think they come from the yield
#     -> eighter check if empty OR somehow find the way to do it properly 
# https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited
# https://blog.miguelgrinberg.com/post/video-streaming-with-flask
# 
import cv2 # https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
import mss # https://python-mss.readthedocs.io/examples.html1
import numpy as np
import threading
import time

class Stream(object):
    # Class variables
    monitor = {}
    thread = None
    frame = None
    lastAccess = 0
    #
    # Constructor
    #
    def __init__(self, monitor):
        if Stream.thread is None:
            print("Constructor: ", monitor)
            Stream.monitor = monitor
            Stream.last_access = time.time() # create a time stamp on construction
            Stream.thread = threading.Thread(target=self._thread) # create Thread
            Stream.thread.start() # start Thread
            while self.getCurrentFrame() is None:
                time.sleep(0)
    #
    # Getter for current frame
    #
    def getCurrentFrame(self):
        '''Get the current frame.'''
        Stream.last_access = time.time() # update the time Stamp with latest Request time
        return Stream.frame
    #
    # Creates the frames 
    # monitor = {'top'      : pixel-pos,
    #            'left'     : pixel-pos,                
    #            'width'    : window-width,
    #            'height'   : window-height
    #           }
    # fps = default 0.5 -> a ss every 2 sek
    #   -> if set to 0 its unlimited
    #
    @staticmethod
    def frames(monitor, fps=0.5):
        if fps == 0: # make sure sleep is set to 0 -> TODO: Benchmark this and check if its nessesary to do more than 1 SS / 2 sek
            sleepTimer = 0
        else: 
            sleepTimer = (1 * (1 // fps)) # make even numberswith mss.mss() as sct:
        with mss.mss() as sct:
            while True:
                time.sleep(sleepTimer)
                print(monitor)
                raw = sct.grab(monitor)
                # encode as a jpeg image  -> https://www.geeksforgeeks.org/python-opencv-imencode-function/
                # encode image into stream data
                # convert stream data into numpy array
                # convert numpy array into bytes
                img = cv2.imencode('.jpg', np.array(raw))[1].tobytes()
                yield(img) # return the Generator
    #
    # method for Thread
    #
    @classmethod
    def _thread(cls, waitTimeOut = 10):
        print('Starting camera thread. waitTimeOut: ', waitTimeOut)
        iterFrames = cls.frames(cls.monitor)
        for frame in iterFrames:
            Stream.frame = frame
            if time.time() - cls.last_access > waitTimeOut: # if there is no user interaction for waitTimeOut end thread
                iterFrames.close()
                print(f'No User conntection for {waitTimeOut}')
                break
        cls.thread = None # close the thread