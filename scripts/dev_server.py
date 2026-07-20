#!/usr/bin/env python3
"""Serve the static demo from the WEB DEMO project root."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class DemoHandler(SimpleHTTPRequestHandler):
    pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 4173), DemoHandler).serve_forever()
