import http.server
import socketserver
import os
from pathlib import Path

PORT = 8088
PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"

class StudioHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        super().end_headers()

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), StudioHTTPRequestHandler) as httpd:
        print(f"Serving {PUBLIC_DIR} at http://127.0.0.1:{PORT}")
        httpd.serve_forever()
