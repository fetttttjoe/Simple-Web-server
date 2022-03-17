import subprocess as sp
from flask import Flask
app = Flask("test")
@app.route('/')
def default():
    return "idk"
@app.route('/example.php')
def phpexample():
    out = sp.run(["php", "example.php"], stdout=sp.PIPE)
    return out.stdout

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, ssl_context=("cert.pem", "key.pem"), debug=True) #prob not the way to go, but since its local i cant care less.