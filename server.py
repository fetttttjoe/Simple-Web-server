from flask import Flask, request, render_template, jsonify
import deviceManager as dM

def inputHandler(userInput):
    temp = userInput.replace(' ', '')
    if temp in dM.VK_CODE:
        dM.keyboardEvent(userInput)
        return 0
    if temp.isalnum():
        for element in userInput:
            if element in dM.VK_CODE:
                dM.keyboardEvent(element)
        return 0
    else:
        return -1 #TODO: Better Error Handling 
        

app = Flask("LazyTool")

@app.route('/')
def default():
    return render_template('default.html')
@app.route('/templates/frame.html', methods=['POST', 'GET'])
def frame():
    if request.method == "POST":
        userInput = request.form['userInput']
        print("Function userInput:",userInput)
    return render_template('frame.html')
@app.route('/templates/inputBox.html', methods=['POST', 'GET'])
def inputBox():
    if request.method == "POST":
        userInput = request.form['userInput']
        inputHandler(userInput)
        print("Function userInput:",userInput)
    return render_template('inputBox.html')    
#testing purpose
@app.route("/test_data")
def names():
    data = {"Command List": ["Search Browser", "Open CMD", "Wtf", "I can't care less"]}
    return jsonify(data)

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, ssl_context=("cert.pem", "key.pem"), debug=True) #prob not the way to go, but since its local i cant care less.