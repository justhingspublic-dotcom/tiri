#!/usr/bin/env python3
"""Serve the static demo from the WEB DEMO project root."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class DemoHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # 開發用：關閉快取，避免改了 css/js 卻看到舊版
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 4173), DemoHandler).serve_forever()
