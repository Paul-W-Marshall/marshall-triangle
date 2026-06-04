import os
import subprocess
import threading
import time

import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.httputil
import tornado.websocket

STREAMLIT_RETRY_ATTEMPTS = 15   # number of tries
STREAMLIT_RETRY_DELAY   = 1.0  # seconds between tries

BYPASS_KEY = os.environ.get("BYPASS_KEY", "")
COOKIE_NAME = "stealth_bypass"
STREAMLIT_PORT = 8501
PUBLIC_PORT = 5000


def start_streamlit():
    time.sleep(2)
    subprocess.Popen(
        [
            "uv", "run", "streamlit", "run", "app.py",
            "--server.port", str(STREAMLIT_PORT),
            "--server.address", "127.0.0.1",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def is_authorized(handler):
    if handler.get_secure_cookie(COOKIE_NAME):
        return True
    key = handler.get_argument("key", None)
    if key and BYPASS_KEY and key == BYPASS_KEY:
        return True
    return False


class GateHandler(tornado.web.RequestHandler):
    """All plain HTTP traffic: show stealth page or proxy to Streamlit."""

    async def _handle(self):
        # Key presented in query string → set cookie and redirect clean
        key = self.get_argument("key", None)
        if key and BYPASS_KEY and key == BYPASS_KEY:
            self.set_secure_cookie(COOKIE_NAME, "1", expires_days=7)
            self.redirect(self.request.path or "/")
            return

        if not is_authorized(self):
            self.render("index.html")
            return

        # Proxy to Streamlit with retry loop
        url = f"http://127.0.0.1:{STREAMLIT_PORT}{self.request.uri}"
        client = tornado.httpclient.AsyncHTTPClient()
        headers = tornado.httputil.HTTPHeaders(self.request.headers)
        headers["Host"] = f"127.0.0.1:{STREAMLIT_PORT}"

        response = None
        for attempt in range(STREAMLIT_RETRY_ATTEMPTS):
            try:
                response = await client.fetch(
                    url,
                    method=self.request.method,
                    headers=headers,
                    body=self.request.body if self.request.body else None,
                    allow_nonstandard_methods=True,
                    follow_redirects=False,
                    raise_error=False,
                    decompress_response=False,  # pass raw bytes; browser decompresses
                )
                break  # success — exit retry loop
            except Exception:
                if attempt < STREAMLIT_RETRY_ATTEMPTS - 1:
                    await tornado.gen.sleep(STREAMLIT_RETRY_DELAY)
                else:
                    self.set_status(503)
                    self.write("App is unavailable — please try again shortly.")
                    return

        self.set_status(response.code)
        # Forward headers cleanly: use set_header (not add_header) to prevent
        # duplicating Tornado's own default headers; Set-Cookie needs add_header
        # to allow multiple cookies. Skip hop-by-hop headers.
        seen = set()
        for name, value in response.headers.get_all():
            lower = name.lower()
            if lower in ("transfer-encoding", "connection"):
                continue
            if lower == "set-cookie":
                self.add_header(name, value)
            elif lower not in seen:
                self.set_header(name, value)
                seen.add(lower)
        if response.body:
            self.write(response.body)

    async def get(self):     await self._handle()
    async def post(self):    await self._handle()
    async def put(self):     await self._handle()
    async def delete(self):  await self._handle()
    async def patch(self):   await self._handle()
    async def options(self): await self._handle()


class WSGateHandler(tornado.websocket.WebSocketHandler):
    """All WebSocket traffic: gate or proxy to Streamlit."""

    async def open(self, *args, **kwargs):
        self._client_terminated = False
        self._upstream = None

        if not is_authorized(self):
            self.close(1008, "not authorized")
            return

        ws_url = f"ws://127.0.0.1:{STREAMLIT_PORT}{self.request.uri}"
        for attempt in range(STREAMLIT_RETRY_ATTEMPTS):
            try:
                self._upstream = await tornado.websocket.websocket_connect(
                    ws_url,
                    on_message_callback=self._on_upstream_message,
                )
                break
            except Exception:
                if attempt < STREAMLIT_RETRY_ATTEMPTS - 1:
                    await tornado.gen.sleep(STREAMLIT_RETRY_DELAY)
                else:
                    self.close(1011, "upstream unavailable")

    def _on_upstream_message(self, message):
        if message is None:
            if not self._client_terminated:
                self.close()
            return
        try:
            self.write_message(message, binary=isinstance(message, bytes))
        except tornado.websocket.WebSocketClosedError:
            pass

    def on_message(self, message):
        if self._upstream:
            self._upstream.write_message(message, binary=isinstance(message, bytes))

    def on_close(self):
        self._client_terminated = True
        if self._upstream:
            self._upstream.close()

    def check_origin(self, origin):
        return True


def make_app():
    cookie_secret = BYPASS_KEY or "fallback-secret-change-me"
    settings = {
        "cookie_secret": cookie_secret,
        "template_path": os.path.dirname(os.path.abspath(__file__)),
        "websocket_ping_interval": 30,
    }
    return tornado.web.Application(
        [
            # Streamlit WebSocket endpoints
            (r"/_stcore/stream", WSGateHandler),
            (r"/stream", WSGateHandler),
            # Everything else (HTTP)
            (r"/.*", GateHandler),
        ],
        **settings,
    )


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    threading.Thread(target=start_streamlit, daemon=True).start()

    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(PUBLIC_PORT)
    print(f"Stealth gate running on port {PUBLIC_PORT}")
    print(f"Streamlit will start internally on port {STREAMLIT_PORT}")
    tornado.ioloop.IOLoop.current().start()
