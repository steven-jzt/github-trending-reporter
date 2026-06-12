"""
DeepSeek API 中转服务器
- 直接运行: python proxy.py
- 部署到云函数: 入口函数 handler()
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError

TARGET = os.getenv("TARGET_URL", "https://api.deepseek.com")
PORT = int(os.getenv("PORT", "8080"))


def forward(method, path, headers, body):
    """转发请求到 DeepSeek，返回 (status, headers, body)"""
    req = Request(
        url=TARGET + path,
        data=body if method == "POST" else None,
        headers={k: v for k, v in headers.items()
                 if k.lower() not in ("host", "transfer-encoding")},
        method=method,
    )
    try:
        resp = urlopen(req, timeout=60)
        return resp.status, dict(resp.headers), resp.read()
    except URLError as e:
        return 502, {}, json.dumps({"error": str(e)}).encode()


# --- 云函数入口 (阿里云 FC / 腾讯云 SCF HTTP 触发器) ---

def handler(environ, start_response):
    """WSGI 入口，部署到云函数时使用"""
    method = environ.get("REQUEST_METHOD", "POST")
    path = environ.get("PATH_INFO", "/")
    body = environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH", 0)))

    headers = {}
    for k, v in environ.items():
        if k.startswith("HTTP_"):
            headers[k[5:].replace("_", "-").title()] = v
    headers["Content-Type"] = environ.get("CONTENT_TYPE", "application/json")

    status_code, resp_headers, resp_body = forward(method, path, headers, body)

    status_str = f"{status_code} OK" if status_code < 400 else f"{status_code} Error"
    start_response(status_str, list(resp_headers.items()))
    return [resp_body]


# --- 独立运行 ---

class _ProxyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        body_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(body_len) if body_len else b""
        status, resp_headers, resp_body = forward(
            "POST", self.path, dict(self.headers), body
        )
        self.send_response(status)
        for k, v in resp_headers.items():
            if k.lower() not in ("transfer-encoding", "content-encoding"):
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(resp_body)

    def log_message(self, fmt, *args):
        print(f"[proxy] {args[0]}")


if __name__ == "__main__":
    print(f"[proxy] forwarding to {TARGET}, port {PORT}")
    HTTPServer(("0.0.0.0", PORT), _ProxyHandler).serve_forever()
