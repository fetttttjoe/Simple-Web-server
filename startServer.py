import os
from tabnanny import verbose
from RemoteControl.app import app
#
# Create Flask app
#
abs_path = os.path.abspath('.')
print(abs_path)
app.template_folder = abs_path + '/templates'
app.static_folder   = abs_path + '/static'
cert = abs_path + '/certificates/cert.pem'
key = abs_path + '/certificates/key.pem'
app.run("0.0.0.0", 5000, ssl_context=(cert, key), debug=True) #prob not the way to go, but since its local i cant care less.
