from queue import Empty
from flask import Flask, request, render_template, jsonify
import deviceManager as dM
#TODO: add blank = enter key (for now), so my lazy ass doesn't need to type enter on enter
#currently only keyboard support, checks if command in VK.Code -> execute, otherwise split and input or return 
def inputToKeyboard(userInput):
    temp = userInput.replace(' ', '')
    if temp in dM.VK_CODE:
        dM.keyboardEvent(userInput)
        return 0
    if temp.isalnum(): #laziest dumb input block possible
        for element in userInput:
            if element in dM.VK_CODE:
                dM.keyboardEvent(element)
        return 0
    else:
        return -1 #TODO: Better Error Handling 


userInputHistory = []
# for now just append the list unlimited with history TODO: use this to get input back (in case you misspelled something)
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

@app.route('/')
def default():
    return render_template('default.html')
@app.route('/templates/frame.html')
def frame():
    return render_template('frame.html')
@app.route('/templates/console.html', methods=['POST', 'GET'])
def inputBox():
    global userInputHistory
    if request.method == "POST":
        userInput = request.form.get('userInput')
        isKeyboardCheckBox = request.form.get('check')
        inputToHistory(userInput)
        #make sure we only send the input to pc if nessesary
        if isKeyboardCheckBox:
            inputToKeyboard(userInput)
        print("Function userInput:",userInput)
    consoleOut = listToString(userInputHistory)
    return render_template('console.html', value=consoleOut)    
#testing purpose
@app.route("/test_data")
def names():
    data = {"Command List": ["Search Browser", "Open CMD", "Wtf", "I can't care less"]}
    return jsonify(data)

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, ssl_context=("cert.pem", "key.pem"), debug=True) #prob not the way to go, but since its local i cant care less.
