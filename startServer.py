import os
from RemoteControl.app import app
#
# Create Flask app
#
absPath = os.path.abspath('.')
app.template_folder = absPath + '/templates'
app.static_folder   = absPath + '/static'
cert = absPath + '/certificates/cert.pem'
key = absPath + '/certificates/key.pem'
app.run("0.0.0.0", 5000, ssl_context=(cert, key), debug=True) #prob not the way to go, but since its local i cant care less.
