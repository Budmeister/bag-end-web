"""Minimal Bag End web service, using only the Python standard library."""

import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


HOME_PAGE = b"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Bag End</title>
  </head>
  <body>
    <main>
      <h1>Hello, world!</h1>
      <p>Bag End is running.</p>
    </main>
  </body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/":
            status, content_type, body = 200, "text/html; charset=utf-8", HOME_PAGE
        elif path == "/healthz":
            status, content_type, body = 200, "application/json", b'{"status":"ok"}\n'
        else:
            status, content_type, body = 404, "text/plain; charset=utf-8", b"Not found\n"

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_HEAD(self):
        self.do_GET()

    def log_message(self, format, *args):
        # Avoid persisting request paths in financial service logs.
        pass


def main():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))
    with ThreadingHTTPServer((host, port), Handler) as server:
        print(f"Bag End listening on {host}:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
