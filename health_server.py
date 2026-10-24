
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BOT_PID_FILE = "/tmp/shrutix_bot.pid"


def bot_is_running():
    try:
        with open(BOT_PID_FILE, "r", encoding="utf-8") as file:
            pid = int(file.read().strip())

        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/health"):
            self.send_response(404)
            self.end_headers()
            return

        running = bot_is_running()
        status = 200 if running else 503
        message = (
            b"Shrutix Music Bot is running!"
            if running
            else b"Music bot is restarting or not running."
        )

        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(message)))
        self.end_headers()
        self.wfile.write(message)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Health server listening on port {port}", flush=True)
    server.serve_forever()
    
