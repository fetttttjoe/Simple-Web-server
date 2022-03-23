from flask import Flask, request, render_template, send_from_directory, redirect, jsonify
import RemoteControl.util.deviceManager as dM
import os, sys

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

userInputHistory = []
#
# Past user Input (only storing Runtime)
# for now just append the list unlimited with history
#
def inputToHistory(userInput):
    global userInputHistory
    if not userInput:
        return
    if userInputHistory:
        userInputHistory.append(userInput)
    else:
        userInputHistory.insert(0, userInput)
#
#transform every element in list into string with newline char
#
def listToString(userInput):
    xstr = '' 
    for element in userInput:
        xstr += f"{element}" + '\n'
    return xstr  
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
    'buttonChannelDown' : 'mouseRight',
}


#
# add the favicon
#
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(f"{app.root_path}/{programName}", 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
#
# default page
#
@app.route('/')
def default():
    return render_template('default.html')

#
# Renders Controller
#
@app.route('/controler.html', methods=['GET', 'POST'])
def controller():
    if request.method == "POST":
        for buttonName, buttonAction in remoteControll.items():
            if request.form.get(f'{buttonName}') == "pressed":
                print(buttonName, buttonAction) #DEBUG
                inputToKeyboard(buttonAction) # just execute the given command (for now)
                return redirect('controler.html')
         # get a better solution to check for user Inputs
        userInput = request.form.get('userInput')
        if userInput is None: 
            print("Button might not be added") #DEBUG
            return redirect('controler.html')
        if userInput == '': # we want the enter key
            userInput = 'enter'
        #
        # lets take -sleep <timer> for now as (userInput)
        #
        if "-sleep" in userInput: # command handler should be implemented
            temp = userInput.split()
            if temp[1].isnumeric(): # fixed on first value for now, i might implement a general input handler later
                dM.shutdownWindows(temp[1])
                inputToHistory(f"System will shut down in {temp[1]} min")
            else:
                print(f"Shutdown Timer: Pls check your Input: {userInput}") #DEBUG
            userInput = None
        if userInput:
            inputToKeyboard(userInput)
            inputToHistory(userInput)
    return render_template('controler.html')
#
# Site for input with "console" field which displays past inputs
#
@app.route('/frame.html')
def consoleInput():
    return render_template('frame.html')

#
# Creates the Input Box to send Commands to Keyboard
#
@app.route('/input.html', methods=['GET', 'POST'])
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
                print(f"Shutdown Timer: Pls check your Input: {userInput}") #DEBUG
            userInput = None
        if userInput:
            inputToHistory(userInput)
            inputToKeyboard(userInput)  
        print("Function inputBox:", userInput) #Debug
    return render_template('input.html')
#
# Displays past inputs
#
@app.route('/console.html', methods=['GET'])
def inputConsole():
    consoleOut = listToString(userInputHistory)
    return render_template( "console.html" , value=consoleOut)    
#
# testing purpose maybe something for later
#
@app.route("/test_data")
def names():
    data = {"Command List": ["Search Browser", "Open CMD", "Wtf", "I can't care less"]}
    return jsonify(data)

if __name__ == '__main__':
    import os
    #
    # Create Flask app
    #
    dirName = os.path.dirname(os.path.abspath(__file__))
    app.template_folder = dirName + '/templates'
    app.static_folder   = dirName + '/static'
    cert = dirName + '/certificates/cert.pem'
    key = dirName + '/certificates/key.pem'
    print(key, cert)
    app.run("0.0.0.0", 5000, ssl_context=(cert, key), debug=True) #prob not the way to go, but since its local i cant care less.
