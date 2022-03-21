from queue import Empty
from flask import Flask, request, render_template, send_from_directory, jsonify
import os
import deviceManager as dM

#checks if command in VK.Code -> execute, otherwise split and input or return 
def inputToKeyboard(userInput):
    match userInput:
        case ' ':
            dM.keyboardEvent('enter')
        case userInput if userInput in dM.VK_CODE:
            dM.keyboardEvent(userInput)
        case userInput if userInput.isalnum():
            for element in userInput:
                if element in dM.VK_CODE:
                    dM.keyboardEvent(element)            
        case _:
            raise ValueError(f"Function inputToKeyboard default case reached {userInput}") #TODO: Better Error Handling 

userInputHistory = []
# for now just append the list unlimited with history
def inputToHistory(userInput):
    global userInputHistory
    if not userInput:
        return
    if userInputHistory:
        userInputHistory.append(userInput)
    else:
        userInputHistory.insert(0, userInput)
#transform every element in list into readable html style
def listToString(userInputHistory):
    xstr = '' 
    for element in userInputHistory:
        xstr += f"{element}" + '\n'
    print("Function listToString",  xstr)
    return xstr  
app = Flask("LazyTool")
#add same favicon for all tabs (for now)
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')
@app.route('/')
def default():
    return render_template('default.html')

# dict for fixed buttons on remote
remoteControll = {
    'buttonBack' : 'back',
}
#add controller_page for now, we will need some kinda input field later (for search etc)
@app.route('/template/controller_page.html', methods=['GET', 'POST'])
def controller():
    if request.method == "POST":
        for buttonName, buttonAction in remoteControll.items():
            if request.form.get(f'{buttonName}') == "pressed":
                inputToKeyboard(buttonAction) # just execute the given command (for now)
    return render_template('controller.html')
@app.route('/templates/frame.html')
def frame():
    return render_template('frame.html')
@app.route('/templates/input.html', methods=['GET', 'POST'])
def inputBox():
    global userInputHistory
    if request.method == "POST":
        sendEvent = request.form.get('Send')
        print(sendEvent)
        userInput = request.form.get('userInput')
        isKeyboardCheckBox = request.form.get('check')
        inputToHistory(userInput)
        #make sure we only send the input to pc if nessesary
        if isKeyboardCheckBox:
            inputToKeyboard(userInput)
        print("Function inputBox:", userInput)
    return render_template('input.html')
@app.route('/templates/console.html', methods=['GET'])
def inputConsole():
    consoleOut = listToString(userInputHistory)
    return render_template('console.html', value=consoleOut)    
#testing purpose
@app.route("/test_data")
def names():
    data = {"Command List": ["Search Browser", "Open CMD", "Wtf", "I can't care less"]}
    return jsonify(data)

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, ssl_context=("cert.pem", "key.pem"), debug=True) #prob not the way to go, but since its local i cant care less.
