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
2. Starts Streamlit as a subprocess on :8501
3. Polls `/_stcore/health` until Streamlit is ready
4. Then transparently proxies all HTTP and WebSocket traffic to :8501

## Critical WebSocket details
- Browser sends `Sec-WebSocket-Protocol` header; proxy must echo it back via `select_subprotocol()` or the handshake fails.
- WebSocket handler must wait for `_ready_event` before opening upstream connection — connecting to Streamlit before it's ready returns 500 and breaks the session.
- Route pattern: `r"/_stcore/stream(?:.*)"` — no capture groups, use `self.request.path` in `open()`.

## Media URL issue
Streamlit embeds media URLs like `http://localhost:PORT/media/...` in WebSocket messages. Fix: pass the original `Host` header through to Streamlit (do NOT strip it in the proxy). Streamlit + uvicorn reads `Host` + `X-Forwarded-Proto` from the request to construct correct media URLs (`https://domain.com/media/...`).

**Why:** `browser.serverAddress` CLI flag causes `http://domain:443/...` (wrong scheme); relying on forwarded headers is cleaner and works for both dev and custom domain.

## Build step
`warmup.py` pre-bakes the matplotlib font cache during the container build so cold starts don't rebuild it (~30 s penalty avoided).

## Deployment type
Must be **Reserved VM** (not Autoscale). Autoscale kills persistent WebSocket connections when idle. Change in Replit Deployments UI — cannot be set via code alone (`.replit` `deploymentTarget = "vm"` is overridden by whatever is selected in the UI at publish time).
