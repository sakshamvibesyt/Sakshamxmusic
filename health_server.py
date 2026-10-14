
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Shrutix Music Bot is running!")

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))

    print(
        f"Health server starting on port {port}",
        flush=True
    )

    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)

    print(
        f"Health server listening on 0.0.0.0:{port}",
        flush=True
    )

    server.serve_forever()
    
