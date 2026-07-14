import os
import subprocess
import sys
import time
import threading
import urllib.request

import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.httputil
import tornado.websocket
import tornado.httpserver
import tornado.gen

STREAMLIT_PORT = 8501
PROXY_PORT = 5000
STREAMLIT_HEALTH = f"http://127.0.0.1:{STREAMLIT_PORT}/_stcore/health"

_streamlit_ready = False
_ready_event = threading.Event()

LOADING_PAGE = b"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="3">
<title>Loading\xe2\x80\xa6</title>
<style>
  body { font-family: sans-serif; display: flex; align-items: center;
         justify-content: center; height: 100vh; margin: 0; }
  p { color: #555; font-size: 1.1rem; }
</style>
</head><body><p>Starting up, please wait\xe2\x80\xa6</p></body></html>"""


def _poll_streamlit():
    global _streamlit_ready
    while True:
        try:
            urllib.request.urlopen(STREAMLIT_HEALTH, timeout=2)
            _streamlit_ready = True
            _ready_event.set()
            print("Streamlit is ready.")
            return
        except Exception:
            time.sleep(1)


class HealthHandler(tornado.web.RequestHandler):
    """Always 200 — lets the deployment probe pass immediately."""
    def get(self):
        self.set_status(200)
        self.write("ok" if _streamlit_ready else "starting")


class ProxyHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ("GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS")

    async def get(self, path=""):       await self._handle(path)
    async def post(self, path=""):      await self._handle(path)
    async def put(self, path=""):       await self._handle(path)
    async def delete(self, path=""):    await self._handle(path)
    async def patch(self, path=""):     await self._handle(path)
    async def head(self, path=""):      await self._handle(path)
    async def options(self, path=""):   await self._handle(path)

    async def _handle(self, path):
        if not _streamlit_ready:
            self.set_status(200)
            self.set_header("Content-Type", "text/html; charset=utf-8")
            self.write(LOADING_PAGE)
            return
        await self._proxy(path)

    async def _proxy(self, path):
        url = f"http://127.0.0.1:{STREAMLIT_PORT}/{path}"
        if self.request.query:
            url += "?" + self.request.query
        headers = {
            k: v for k, v in self.request.headers.get_all()
            if k.lower() not in ("connection",)
        }
        client = tornado.httpclient.AsyncHTTPClient()
        try:
            resp = await client.fetch(
                tornado.httpclient.HTTPRequest(
                    url,
                    method=self.request.method,
                    headers=headers,
                    body=self.request.body or None,
                    allow_nonstandard_methods=True,
                    decompress_response=True,
                    follow_redirects=False,
                )
            )
        except tornado.httpclient.HTTPClientError as e:
            if e.response:
                resp = e.response
            else:
                self.set_status(502)
                self.write(b"Bad gateway")
                return
        self.set_status(resp.code)
        for k, v in resp.headers.get_all():
            if k.lower() not in ("transfer-encoding", "connection",
                                  "content-encoding", "content-length"):
                self.set_header(k, v)
        if resp.body:
            self.write(resp.body)


class WSProxyHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def select_subprotocol(self, subprotocols):
        return subprotocols[0] if subprotocols else None

    async def open(self):
        self._upstream = None
        # Wait up to 90 s for Streamlit to be ready before connecting upstream
        if not _streamlit_ready:
            await tornado.ioloop.IOLoop.current().run_in_executor(
                None, lambda: _ready_event.wait(timeout=90)
            )
        if not _streamlit_ready:
            self.close(1013, "Server not ready")
            return
        path = self.request.path.lstrip("/")
        url = f"ws://127.0.0.1:{STREAMLIT_PORT}/{path}"
        if self.request.query:
            url += "?" + self.request.query

        # Forward the original Host + X-Forwarded-* headers so Streamlit
        # builds correct media URLs (https://domain/media/…) instead of
        # http://127.0.0.1:8501/media/…
        skip = {
            "connection", "upgrade",
            "sec-websocket-key", "sec-websocket-version",
            "sec-websocket-extensions", "sec-websocket-protocol",
        }
        forward = tornado.httputil.HTTPHeaders()
        for k, v in self.request.headers.get_all():
            if k.lower() not in skip:
                forward.add(k, v)
        # Ensure downstream knows the public scheme
        if "X-Forwarded-Proto" not in forward:
            forward["X-Forwarded-Proto"] = "https"

        ws_req = tornado.httpclient.HTTPRequest(url, headers=forward)
        try:
            self._upstream = await tornado.websocket.websocket_connect(
                ws_req,
                on_message_callback=self._from_upstream,
            )
        except Exception as e:
            print(f"WS upstream connect failed: {e}")
            self.close(1011, "Upstream error")

    def _from_upstream(self, message):
        if message is None:
            self.close()
        else:
            try:
                self.write_message(message, binary=isinstance(message, bytes))
            except tornado.websocket.WebSocketClosedError:
                pass

    def on_message(self, message):
        if self._upstream:
            try:
                self._upstream.write_message(message, binary=isinstance(message, bytes))
            except tornado.websocket.WebSocketClosedError:
                pass

    def on_close(self):
        if self._upstream:
            self._upstream.close()


def start_streamlit():
    subprocess.Popen(
        [
            "uv", "run", "streamlit", "run", "app.py",
            "--server.port", str(STREAMLIT_PORT),
            "--server.address", "127.0.0.1",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
        ]
    )
    _poll_streamlit()


def make_app():
    return tornado.web.Application([
        (r"/_stcore/stream(?:.*)", WSProxyHandler),
        (r"/healthz",             HealthHandler),
        (r"/(.*)",                ProxyHandler),
    ])


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"Proxy on :{PROXY_PORT} — launching Streamlit on :{STREAMLIT_PORT}")
    threading.Thread(target=start_streamlit, daemon=True).start()
    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(PROXY_PORT, address="0.0.0.0")
    tornado.ioloop.IOLoop.current().start()
