import os
import subprocess
import sys
import time
import threading
import urllib.request
import json
import collections

import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.httputil
import tornado.websocket
import tornado.httpserver
import tornado.gen

STREAMLIT_PORT = 8501
PROXY_PORT = 5000

# ---------------------------------------------------------------------------
# Download-code validation state (in-memory, single-process)
# ---------------------------------------------------------------------------
_MAX_ATTEMPTS   = 5          # failed attempts before lockout
_WINDOW_SECONDS = 15 * 60   # rolling window: 15 minutes
_LOCKOUT_SECONDS = 15 * 60  # how long the lockout lasts

# Maps IP -> deque of failure timestamps (epoch floats)
_failed_attempts: dict = collections.defaultdict(collections.deque)
# Maps IP -> lockout-expiry timestamp (epoch float); absent means not locked
_lockouts: dict = {}

_INTERNAL_IP_HEADER = "X-Replit-Client-IP"   # injected by Tornado; never trusted from clients

def _extract_real_ip(request) -> str:
    """Return the real client IP from X-Forwarded-For (last entry, set by Replit's ingress).

    Replit's ingress layer *appends* the real client IP to X-Forwarded-For, so
    reading the last entry defeats header-injection attempts from the client.
    Falls back to request.remote_ip when no XFF header is present (local dev).
    """
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        # Last entry is added by the closest trusted proxy (Replit's ingress)
        return xff.split(",")[-1].strip()
    return request.remote_ip or "unknown"

def _is_locked_out(ip: str) -> float:
    """Return seconds remaining in lockout, or 0 if not locked out."""
    expiry = _lockouts.get(ip, 0)
    remaining = expiry - time.time()
    if remaining > 0:
        return remaining
    # Expired — clean up
    _lockouts.pop(ip, None)
    return 0

def _record_failure(ip: str) -> None:
    """Record a failed attempt; impose lockout if threshold exceeded."""
    now = time.time()
    dq = _failed_attempts[ip]
    # Prune entries outside the rolling window
    cutoff = now - _WINDOW_SECONDS
    while dq and dq[0] < cutoff:
        dq.popleft()
    dq.append(now)
    if len(dq) >= _MAX_ATTEMPTS:
        _lockouts[ip] = now + _LOCKOUT_SECONDS
        dq.clear()

def _reset_attempts(ip: str) -> None:
    """Clear failure history on successful validation."""
    _failed_attempts.pop(ip, None)
    _lockouts.pop(ip, None)


# ---------------------------------------------------------------------------
# Per-IP rate limiting (in-memory, sliding window)
# ---------------------------------------------------------------------------
_RATE_LIMIT_RPS   = int(os.environ.get("RATE_LIMIT_RPS",   "10"))  # max req/s sustained
_RATE_LIMIT_BURST = int(os.environ.get("RATE_LIMIT_BURST", "30"))  # max req in 5 s window

# Maps IP -> deque of request timestamps (epoch floats)
_rate_timestamps: dict = collections.defaultdict(collections.deque)

def _is_rate_limited(ip: str) -> bool:
    """Sliding-window rate limiter.

    Returns True (block) if the IP has exceeded either:
      - _RATE_LIMIT_RPS requests in the last 1 second, OR
      - _RATE_LIMIT_BURST requests in the last 5 seconds.
    """
    now = time.time()
    dq = _rate_timestamps[ip]

    # Prune entries older than 5 seconds (longest window we care about)
    cutoff5 = now - 5.0
    while dq and dq[0] < cutoff5:
        dq.popleft()

    # Count requests in the last 5 s (burst window)
    burst_count = len(dq)

    # Count requests in the last 1 s (sustained window)
    cutoff1 = now - 1.0
    rps_count = sum(1 for t in dq if t >= cutoff1)

    if rps_count >= _RATE_LIMIT_RPS or burst_count >= _RATE_LIMIT_BURST:
        return True

    dq.append(now)
    return False


STREAMLIT_HEALTH = f"http://127.0.0.1:{STREAMLIT_PORT}/_stcore/health"

_streamlit_ready = False
_ready_event = threading.Event()

LOADING_PAGE = b"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="1">
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


class ValidateCodeHandler(tornado.web.RequestHandler):
    """POST /api/validate-code — server-side download-code validation with rate limiting."""

    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")

    def post(self):
        # Only allow calls from localhost (Streamlit). External callers get 403
        # so they cannot probe the endpoint or spoof the client-IP header.
        if self.request.remote_ip not in ("127.0.0.1", "::1"):
            self.set_status(403)
            self.write(json.dumps({"ok": False, "error": "forbidden"}))
            return

        # Read the real client IP that Streamlit extracted from X-Replit-Client-IP
        # (which Tornado injected; the client can never supply it directly).
        ip = self.request.headers.get("X-Client-IP", "unknown")
        if not ip or ip == "unknown":
            self.set_status(400)
            self.write(json.dumps({"ok": False, "error": "missing_client_ip"}))
            return

        # Check lockout first
        remaining = _is_locked_out(ip)
        if remaining > 0:
            retry_after = int(remaining) + 1
            self.set_header("Retry-After", str(retry_after))
            self.set_status(429)
            self.write(json.dumps({
                "ok": False,
                "error": "too_many_attempts",
                "retry_after": retry_after,
            }))
            return

        # Parse submitted code
        try:
            body = json.loads(self.request.body)
            submitted = str(body.get("code", "")).strip()
        except (ValueError, TypeError):
            self.set_status(400)
            self.write(json.dumps({"ok": False, "error": "bad_request"}))
            return

        # Load valid codes from environment secret (comma-separated list supported)
        raw_secret = os.environ.get("DOWNLOAD_CODE", "")
        valid_codes = {c.strip() for c in raw_secret.split(",") if c.strip()}

        if submitted and submitted in valid_codes:
            _reset_attempts(ip)
            self.set_status(200)
            self.write(json.dumps({"ok": True}))
        else:
            _record_failure(ip)
            self.set_status(401)
            self.write(json.dumps({"ok": False, "error": "invalid_code"}))


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
        # Rate-limit check before any proxying
        ip = _extract_real_ip(self.request)
        if _is_rate_limited(ip):
            self.set_status(429)
            self.set_header("Retry-After", "1")
            self.set_header("Content-Type", "application/json")
            self.write('{"error":"rate_limit_exceeded"}')
            return

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
            if k.lower() not in ("connection", _INTERNAL_IP_HEADER.lower())
        }
        # Inject trusted real client IP so Streamlit can use it for rate-limiting
        headers[_INTERNAL_IP_HEADER] = _extract_real_ip(self.request)
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
            _INTERNAL_IP_HEADER.lower(),   # strip any client-supplied value
        }
        forward = tornado.httputil.HTTPHeaders()
        for k, v in self.request.headers.get_all():
            if k.lower() not in skip:
                forward.add(k, v)
        # Inject trusted real client IP so st.context.headers sees it
        forward[_INTERNAL_IP_HEADER] = _extract_real_ip(self.request)
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
        (r"/healthz",              HealthHandler),
        (r"/api/validate-code",    ValidateCodeHandler),
        (r"/(.*)",                 ProxyHandler),
    ])


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"Proxy on :{PROXY_PORT} — launching Streamlit on :{STREAMLIT_PORT}")
    threading.Thread(target=start_streamlit, daemon=True).start()
    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(PROXY_PORT, address="0.0.0.0")
    tornado.ioloop.IOLoop.current().start()
