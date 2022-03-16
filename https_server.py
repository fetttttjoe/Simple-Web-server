#idk about that solution, i will leave it here, but i am NOT happy with that (and its not working....)

import http.server
import ssl

class SimpleHTTPS:
    def __init__(self, address):
        self.address = address
        self.httpd = http.server.HTTPServer(self.address, http.server.SimpleHTTPRequestHandler)
        self.httpd.socket = ssl.wrap_socket(self.httpd.socket,
                               server_side=True,
                               certfile="cert.pem",
                               keyfile="key.pem",
                               ssl_version=ssl.PROTOCOL_TLS)
    def Test():
        return "<h1 style='color:red'> Testing Flask server </h1>"

if __name__ == "__main__":
    server_address = ("0.0.0.0", 443)
    server = SimpleHTTPS(server_address)
    server.httpd.serve_forever()

