"""
DeepSeek API 中转服务器
部署到国内云函数后，GitHub Actions 通过这个地址访问 DeepSeek
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

import httpx

TARGET = os.getenv("TARGET_URL", "https://api.deepseek.com")
PORT = int(os.getenv("PORT", "8080"))


class Proxy(BaseHTTPRequestHandler):
    def do_POST(self):
        body_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(body_len) if body_len else b""

        headers = {}
        for k, v in self.headers.items():
            if k.lower() not in ("host", "transfer-encoding"):
                headers[k] = v

        try:
            resp = httpx.request(
                method="POST",
                url=TARGET + self.path,
                headers=headers,
                content=body,
                timeout=60,
            )
            self.send_response(resp.status_code)
            for k, v in resp.headers.items():
                if k.lower() not in ("transfer-encoding", "content-encoding"):
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(resp.content)
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def log_message(self, fmt, *args):
        print(f"[proxy] {args[0]}")


if __name__ == "__main__":
    print(f"[proxy] forwarding to {TARGET}, port {PORT}")
    HTTPServer(("0.0.0.0", PORT), Proxy).serve_forever()
