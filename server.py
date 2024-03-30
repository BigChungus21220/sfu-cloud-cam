# hosts the site for viewing the current data

from http.server import SimpleHTTPRequestHandler
import socketserver

hostName = "localhost"
serverPort = 8080

class MyHttpRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

def start(queue):
    handler_object = MyHttpRequestHandler
    server = socketserver.TCPServer(("", serverPort), handler_object)
    print("Hosting on http://localhost:8080/")
    server.serve_forever()