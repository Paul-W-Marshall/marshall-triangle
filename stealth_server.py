from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class StealthHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.path = '/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(('0.0.0.0', 5000), StealthHandler)
    print('Stealth mode server running on port 5000')
    server.serve_forever()
