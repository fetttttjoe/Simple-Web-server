from flask import Flask, jsonify

app = Flask(__name__)

#root folder
@app.route("/")
def index():
    return '<h1 style="text-align:center;color:red">This is a simple test to check if Flask is running Properly</h1'

@app.route("/test_data")
def names():
    data = {"Random List": ["IDK", "Dave ist doof", "Wtf", "I can't care less"]}
    return jsonify(data)


if __name__ == "__main__":
    app.run(ssl_context=("cert.pem", "key.pem"), debug=True) #prob not the way to go, but since its local i cant care less.