---
name: Streamlit proxy for VM deployment
description: How to make Streamlit pass Replit VM health checks and serve correctly behind a Tornado proxy.
---

# Streamlit VM Deployment Proxy

## The rule
Streamlit takes 10–20 s to start (heavy imports: numpy, PIL, scipy, matplotlib). Replit's VM health check probes `GET /` and fails the deploy if it doesn't get 200 within the timeout. **Running Streamlit directly on port 5000 always fails the promote step.**

## The fix
`stealth_server.py` runs a Tornado proxy on :5000 that:
1. Returns HTTP 200 ("starting") immediately — health check passes
2. Starts Streamlit as a subprocess on :8501 using `uv run streamlit`
3. Polls `/_stcore/health` until Streamlit is ready
4. Then transparently proxies all HTTP and WebSocket traffic to :8501

## Run command — must use uv
Both the workflow and the deployment `run` command must be `uv run python stealth_server.py`, NOT bare `python stealth_server.py`. Bare `python` in the VM deployment environment does not have access to the uv virtualenv packages (tornado, etc.).

**Why:** `deployConfig` and `configureWorkflow` both need to be updated with `["uv", "run", "python", "stealth_server.py"]`.

## Gzip / Content-Length bug
When proxying Streamlit responses with `decompress_response=True` (Tornado decompresses gzip for you), you MUST also strip `content-length` from the forwarded headers. The original `Content-Length` is the compressed size; after decompression the body is larger, so forwarding the old header causes `HTTPOutputError: Tried to write more data than Content-Length`.

**Fix:** Strip `("transfer-encoding", "connection", "content-encoding", "content-length")` from proxied response headers. Tornado then sets the correct Content-Length based on the actual body.

## Critical WebSocket details
- Browser sends `Sec-WebSocket-Protocol` header; proxy must echo it back via `select_subprotocol()` or the handshake fails.
- WebSocket handler must wait for `_ready_event` before opening upstream connection — connecting to Streamlit before it's ready returns 500 and breaks the session.
- Route pattern: `r"/_stcore/stream(?:.*)"` — no capture groups, use `self.request.path` in `open()`.
- Forward original `Host` and `X-Forwarded-Proto` headers in the upstream websocket_connect call (via `HTTPRequest(url, headers=forward)`). Without this, Streamlit sees `Host: 127.0.0.1:8501` and generates `http://127.0.0.1:8501/media/…` URLs the browser can't reach.

## Media URL issue
Streamlit embeds media URLs in WebSocket messages based on the Host header it receives. Forward `Host: <public-domain>` and `X-Forwarded-Proto: https` to Streamlit in the WebSocket upstream connection. Add a fallback `if "X-Forwarded-Proto" not in forward: forward["X-Forwarded-Proto"] = "https"`.

**Why:** `browser.serverAddress` CLI flag causes `http://domain:443/...` (wrong scheme); relying on forwarded headers works for both dev and production custom domain.

## Build step
`warmup.py` pre-bakes the matplotlib font cache during the container build so cold starts don't rebuild it (~30 s penalty avoided).

## Deployment type
Must be **Reserved VM** (not Autoscale). With autoscale, each instance has its own `_streamlit_ready = False` state. If a browser loads the initial HTML from Instance A (ready) but fetches JS files from Instance B (still starting), Instance B returns `text/html` loading page for all paths. JS module strict MIME checking then rejects them — the whole Streamlit UI fails to load. Set via `deployConfig({ deploymentTarget: "vm", ... })`.
