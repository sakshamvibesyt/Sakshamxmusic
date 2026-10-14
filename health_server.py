
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Shrutix Music Bot is running!")

    def log_message(self, format, *args):
        pass

port = int(os.environ.get("PORT", "10000"))
server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
server.serve_forever()
