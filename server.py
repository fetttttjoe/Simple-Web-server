from flask import Flask, request, render_template, send_from_directory, jsonify
import os
import deviceManager as dM
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
def listToString(userInputHistory):
    xstr = '' 
    for element in userInputHistory:
        xstr += f"{element}" + '\n'
    print("Function listToString",  xstr)
    return xstr  
#
# dict for fixed buttons on remote (name : keyboardcommand)
#
remoteControll = {
    'buttonMute'        : 'mute',
    'buttonBack'        : 'back',
    'buttonVolumeUp'    : 'volumeUp',
    'buttonVolumeDown'  : 'volumeDown',
    'buttonArrowUp'     : 'arrowUp',
    'buttonArrowDown'   : 'arrowDown',
    'buttonArrowLeft'   : 'arrowLeft',
    'buttonArrowRight'  : 'arrowRight',
}


#
# Create Flask app
#
app = Flask("LazyTool")
#
# add the favicon
#
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')
#
# default page
#
@app.route('/')
def default():
    return render_template('default.html')
#
# Frame to hold Console and Control unit
#
@app.route('/controler_page.html')
def consoleControl():
    return render_template('controler_page.html')
#
# Renders Controller
#
@app.route('/controler.html', methods=['GET', 'POST'])
def controller():
    if request.method == "POST":
        for buttonName, buttonAction in remoteControll.items():
            if request.form.get(f'{buttonName}') == "pressed":
                inputToKeyboard(buttonAction) # just execute the given command (for now)
        #
        # lets take -sleep <timer> for now as (userInput)
        #
        userInput = request.form.get('userInput')
        if userInput:
            inputToHistory(userInput)
            if userInput.lower() == "enter":
                inputToKeyboard('enter')
            elif "-sleep" in userInput:
                temp = userInput.split()
                if temp[1].isalnum():  # fixed on first value for now, i might implement a general input handler later
                    dM.shutdownWindows(temp[1]) #i will rework this as soon as we get some more options
                else:
                    print(f"Shutdown Timer: Pls check your Input {userInput}")
            else:
                inputToKeyboard(userInput)
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
            print(temp)
            if temp[1].isalnum(): # fixed on first value for now, i might implement a general input handler later
                dM.shutdownWindows(temp[1])
            else:
                print(f"Shutdown Timer: Pls check your Input {userInput}")
        inputToHistory(userInput)
        inputToKeyboard(userInput)
        print("Function inputBox:", userInput)
    return render_template('input.html')
#
# Displays past inputs
#
@app.route('/console.html', methods=['GET'])
def inputConsole():
    consoleOut = listToString(userInputHistory)
    return render_template('console.html', value=consoleOut)    
#
# testing purpose maybe something for later
#
@app.route("/test_data")
def names():
    data = {"Command List": ["Search Browser", "Open CMD", "Wtf", "I can't care less"]}
    return jsonify(data)

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, ssl_context=("cert.pem", "key.pem"), debug=True) #prob not the way to go, but since its local i cant care less.
