import multiprocessing
from tarfile import StreamError
from flask import Flask, request, render_template, send_from_directory, redirect, jsonify, url_for, Response
import os, sys
import RemoteControl.util.deviceManager as dM
from RemoteControl.util.stream import Stream
import time
import logging
import mss 
#
# generates a list containing informations about the connected monitors
#
def genMonitors():
    monitors = []
    with mss.mss() as sct:
        print(len(sct.monitors))
        for num,monitor in enumerate(sct.monitors):
            if num == 0: #skip full screen view
                continue
            monitors.append(monitor)
            print(f"Monitor with Dimensions: {monitor} found") #DEBUG
    return monitors
#
# Function to generate the Stream Objects
#
def genStreamObjects():
    global STREAMOBJECTS
    monitors = genMonitors()
    print("genStreamObjects Monitors:", monitors)
    for id in range(0, len(monitors)):
        info = monitors[id]
        print("genStreamObjects Info:", info)
        streamObj = Stream(info)
        STREAMOBJECTS.append(streamObj)

# Global Variables 
STREAMOBJECTS = [] 
# global UserInputHistory
USERINPUTHISTORY = []
with mss.mss() as sct:
    if len(sct.monitors) != len(STREAMOBJECTS):
        #
        # call this Once to generate the Stream objects
        #
        genStreamObjects() 

#
# Program Name (also used for path), this needs to be done in a smarter way.
#   idk why relative inputs wont let me pull the name from setup.py
#
programName = "RemoteControl"
#
# Initialise Flask app
# 
app = Flask("LazyTool")
#
# Sends user Input to Keyboard 
# Checks if command in VK.Code -> execute, otherwise split and input or return 
#
def inputToKeyboard(userInput):
    match userInput:
        case ' ':
            dM.keyboardEvent('enter')
        case userInput if userInput in dM.VK_CODE:
            dM.keyboardEvent(userInput)
        case _: # this might be dangerous, but will work for now.
            for element in userInput:
                if element in dM.VK_CODE:
                    dM.keyboardEvent(element)            

#
# Past user Input (only storing Runtime)
# for now just append the list unlimited with test<history
#
def inputToHistory(userInput):
    global USERINPUTHISTORY
    if not userInput:
        return
    if USERINPUTHISTORY:
        USERINPUTHISTORY.append(userInput)
    else:
        USERINPUTHISTORY.insert(0, userInput)
#
#transform every element in list into string with newline char
#
def listToString(userInput):
    temp = '<strong class=consoleOut>' 
    for element in userInput:
        temp += f"{element}<br>" 
    temp += '</strong>' # TEXT MUST BE STROOOONG
    return temp  
#
# dict for fixed buttons on remote (buttonname : keyboardcommand)
#
remoteControll = {
    'buttonBack'        : 'back',
    'buttonEnter'       : 'enter',
    'buttonMute'        : 'mute',
    'buttonVolumeUp'    : 'volumeUp',
    'buttonVolumeDown'  : 'volumeDown',
    'buttonArrowUp'     : 'arrowUp',
    'buttonArrowDown'   : 'arrowDown',
    'buttonArrowLeft'   : 'arrowLeft',
    'buttonArrowRight'  : 'arrowRight',
    'buttonHome'        : None,
    'buttonChannelUp'   : None, 
    'buttonChannelDown' : None, 
    'buttonPower'       : None,
    'buttonInput'       : None,
    'buttonControl'     : None,
    'buttonMenu'        : None,
    'buttonNumeric'     : None, #i dont really need this revamp
    'buttonDots'        : None,
}
# default page
#
@app.route('/')
def default():
    return render_template('default.html')
#
# Renders Controller
#
@app.route('/controler', methods=['GET', 'POST'])
def controler():
    logging.debug(request) # DEBUG
    if request.method == "POST":
        # get a better solution to check for user Inputs
        userInput = request.form.get('userInput')  
        if userInput:
            if userInput == '': # we want the enter key
                userInput = 'enter'
            #
            # lets take -sleep <timer> for now as (userInput)
            #
            if "-sleep" in userInput: # command handler should be implemented
                temp = userInput.split()
                if (len(temp)) == 1: # catch if only "-sleep" in input
                    inputToHistory(f"The correct format for this Command is: -sleep 'min'")
                    inputToHistory("\texample: -sleep 10")
                    return redirect(url_for('controler'))
                if temp[1].isnumeric(): # fixed on first value for now, i might implement a general input handler later
                    retCode = dM.shutdownWindows(temp[1])
                    if retCode == 0: # error code = 0 -> everything work or timer already set and aborted 
                        inputToHistory(f"System will shut down in {temp[1]} min.")
                    else:
                        inputToHistory(f"System returned Error Code: {retCode}.") #User Out
                        logging.debug(f"System returned Error Code: {retCode}.")          #DEBUG
                    return redirect(url_for('controler'))     
                elif temp[1] == 'a': # -sleep a -> abort sleep timer on system.
                    retCode = dM.abortShutdownWindows()
                    if retCode == 0: 
                        inputToHistory("Shutdown aborted!")              
                    else:
                        inputToHistory(f"System returned Error Code: {retCode}.")
                    return redirect(url_for('controler'))     
                else:
                    print(f"Shutdown Timer: Pls check your Input: {userInput}.") #DEBUG
                    inputToHistory(f"Shutdown Timer: Pls check your Input: {userInput}.")
                return redirect(url_for('controler'))
            inputToKeyboard(userInput)
            inputToHistory(userInput)
            return redirect(url_for('controler'))
        for buttonName, buttonAction in remoteControll.items():
            if request.form.get(f'{buttonName}') == "pressed":
                print(buttonName, buttonAction) #DEBUG
                if buttonAction is None: 
                    logging.debug("Button might not be added") #DEBUG
                else:
                    inputToKeyboard(buttonAction) # just execute the given command (for now)
                return redirect(url_for('controler'))
    return render_template('controler.html')
#
# Site for input with "console" field which displays past inputs
#
@app.route('/frame')
def consoleInput():
    return render_template('frame.html')

#
# Creates the Input Box to send Commands to Keyboard
#
@app.route('/input', methods=['GET', 'POST'])
def inputBox():
    global userInputHistory
    if request.method == "POST":
        userInput = request.form.get('userInput')
        #
        # lets take -sleep <timer> for now as (userInput)
        #
        if "-sleep" in userInput:
            temp = userInput.split()
            if temp[1].isnumeric(): # fixed on first value for now, i might implement a general input handler later
                dM.shutdownWindows(temp[1])
                inputToHistory(f"System will shut down in {temp[1]} min")
            else:
                logging.debug(f"Shutdown Timer: Pls check your Input: {userInput}") #DEBUG
            userInput = None
        if userInput:
            inputToHistory(userInput)
            inputToKeyboard(userInput)  
        logging.debug("Function inputBox:", userInput) #Debug
    return render_template('input.html')
#
# Displays past inputs
#
@app.route('/console.html', methods=['GET'])
def console():
    consoleOut = listToString(userInputHistory)
    return render_template( "console.html" , value=consoleOut)    
                    
#
# TESTING AREA
# First try on "video Stream"
#     

@app.route('/video')
def streams():
    return render_template('stream.html')
#
# testing purpose maybe something for later
#
@app.route("/test_data")
def names():
    data = {"Command List": ["Search Browser", "Open CMD", "Wtf", "I can't care less"]}
    return jsonify(data)


####################################################################################################################                                                                                                                                                                           
# TODO: FUTURE STUFF (maybe)
# Generate the Generator Object for frames
# https://stackoverflow.com/questions/59554042/handle-multiple-cameras-using-flask-and-opencv
#
#def genFrames(monitorId = 0):
#    streamObjects = genStreamObjects()
#    streamObj = streamObjects[monitorId]
#    print("genFrames: ", streamObjects[monitorId])
#    while True:
#        frame = streamObj.getCurrentFrame() # read the current frame from obj
#        yield (b'--frame\r\n'
#               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#
# maybe this is better for stream Testing needed
#def stream_template(template_name, **context):                                                                                                                                                 
#    app.update_template_context(context)                                                                                                                                                       
#    t = app.jinja_env.get_template(template_name)                                                                                                                                              
#    rv = t.stream(context)                                                                                                                                                                     
#    rv.enable_buffering(5)                                                                                                                                                                   
#    return rv       
####################################################################################################################                                                                                                                                                                           
#
# Generate stream for flask
#
def generate():   
    #streamObjects = genStreamObjects()   
    global STREAMOBJECTS
    generator = STREAMOBJECTS[0]
    generator.startStream()
    while True:                                                                                                                                                                                                                                                                                                                       
        logging.debug(f"generate() With object Id: [{generator.id}]")
        logging.debug(f"\t Monitoring:{generator.monitor}")
        currentFrame = generator.getCurrentFrame()
        if currentFrame is None:
            logging.debug("Explain?")
            time.sleep(1)
            continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + currentFrame + b'\r\n')   
        time.sleep(.5)
#
# Test function to simulate 2nd request for stream
#
def generate1():   
    global STREAMOBJECTS
    generator = STREAMOBJECTS[1]
    generator.startStream()
    while True:                                                                                                                                                                                                                                                                                                                       
        logging.debug(f"generate() With object Id: [{generator.id}]")   # DEBUG
        logging.debug(f"\t Monitoring:{generator.monitor}")             # DEBUG
        currentFrame = generator.getCurrentFrame()
        if currentFrame is None:
            logging.debug("Explain?")
            continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + currentFrame + b'\r\n')   
        time.sleep(.5)
@app.route('/stream')                                                                                                                                                                          
def stream_view():                                                                                                                                                                             
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame' )              
@app.route('/stream1')    
def stream_view1():                                                                                                                                                                             
    time.sleep(.5) # delay it a bit for now to make sure its 2nd source                                                                                                                                                                       
    return Response(generate1(), mimetype='multipart/x-mixed-replace; boundary=frame' )  
if __name__ == '__main__':
    #
    # Create Flask app
    #
    from datetime import datetime
    dirName = os.path.dirname(os.path.abspath(__file__))
    app.template_folder = dirName + '/templates'
    app.static_folder   = dirName + '/static'
    cert = dirName + '/certificates/cert.pem'
    key = dirName + '/certificates/key.pem'

    logging.basicConfig(    filename= "debug.log", #filename= f"Debug{str(datetime.now()).replace(' ', '').replace(':', '.')}.log"
                            filemode='a',
                            encoding='utf-8',
                            format="{processName:<12} {message} ({filename}:{lineno})", style="{",
                            level=logging.DEBUG,
                            force=True)
    app.run("0.0.0.0", 5000, ssl_context=(cert, key), threaded=True, debug=True) #prob not the way to go, but since its local i cant care less.
    