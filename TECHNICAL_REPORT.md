# Marshall Triangle — Technical Report

**Author:** Paul W. Marshall
**Entity:** Fidelitas LLC
**Date:** May 2026
**Version:** 1.0

---

## 1. Project Overview

Marshall Triangle is a geometric visualization framework for representing triadic balance in complex systems. It maps three competing concerns — Privacy, Performance, and Personalization — to color sources at the midpoints of an equilateral triangle and renders their interaction using radial Gaussian falloff. The result is a continuously graded color field that communicates the relative weight of each concern at a glance.

The project is deployed as a Streamlit web application behind a Tornado-based access gate, and is registered as an on-chain IP asset via Story Protocol (`marshall_triangle-v1-sovereign`).

---

## 2. System Architecture

### 2.1 Component Overview

```
Public Internet
      │
      ▼
┌─────────────────────────────┐
│  Tornado Stealth Gate       │  port 5000  (public)
│  stealth_server.py          │
│  ── cookie / key auth       │
│  ── HTTP proxy              │
│  ── WebSocket proxy         │
└────────────┬────────────────┘
             │  authorized traffic only
             ▼
┌─────────────────────────────┐
│  Streamlit Application      │  port 8501  (internal)
│  app.py                     │
│  ── UI / session state      │
│  ── HarmonyIndex calls      │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  HarmonyIndex Engine        │
│  harmony_index.py           │
│  ── Gaussian rendering      │
│  ── Triadic Calibration     │
│  ── Adaptive Sigma          │
└─────────────────────────────┘
```

### 2.2 Stealth Gate (stealth_server.py)

The stealth gate is a Tornado async HTTP server that runs on port 5000 — the only publicly exposed port. It serves two purposes: access control and transparent proxying.

**Authorization flow:**

1. A visitor arrives without credentials → the server renders `index.html` (the stealth curtain).
2. A visitor arrives with `?key=<BYPASS_KEY>` → the server validates the key against the `BYPASS_KEY` environment secret, sets a signed secure cookie (`stealth_bypass`, 7-day expiry), and redirects to the same path without the query parameter.
3. A visitor with a valid cookie → all HTTP and WebSocket traffic is proxied to the internal Streamlit instance on `127.0.0.1:8501`.

**Proxy behavior:**

- HTTP requests are proxied via `tornado.httpclient.AsyncHTTPClient` with method, headers, and body forwarded verbatim. `transfer-encoding`, `content-encoding`, and `connection` headers are stripped before forwarding the response to avoid framing errors.
- WebSocket connections on `/_stcore/stream` and `/stream` are proxied via `tornado.websocket.websocket_connect`, with bidirectional message forwarding. Binary and text frames are both supported.
- Streamlit is launched as a subprocess (`uv run streamlit run app.py`) on server startup, bound to `127.0.0.1:8501` with CORS and XSRF protection disabled (safe because it is not directly reachable from the internet).

**Security properties:**

- The `BYPASS_KEY` is stored exclusively as a Replit environment secret — never in source code or the lockfile.
- The same key is used as the Tornado `cookie_secret` so signed cookies cannot be forged without knowledge of the key.
- Rotating the key immediately invalidates all existing cookies.
- The internal Streamlit port (8501) is not exposed in the Replit deployment configuration.

### 2.3 Streamlit Application (app.py)

The application is stateless — all user data lives in Streamlit session state and is discarded on page reload. There is no database.

**Session state variables:**

| Key | Type | Description |
|-----|------|-------------|
| `privacy_strength` | float [0,1] | Red channel weight |
| `performance_strength` | float [0,1] | Green channel weight |
| `personalization_strength` | float [0,1] | Blue channel weight |
| `sigma` | float | Base Gaussian sigma |
| `intensity` | float | Falloff amplitude |
| `edge_blur` | float | Post-render edge softening radius |
| `edge_factor` | float | Edge pixel dimming factor |
| `size` | int | Render resolution (px) |
| `falloff_type` | str | `gaussian` or `inverse_square` |
| `calibration` | dict | White point `{r, g, b}` |
| `marshall_states` | dict | Named saved states with thumbnails |
| `rendering_presets` | dict | Named rendering parameter sets |

**UI layout:**

The app renders the triangle immediately on load using default parameters, then provides three navigation tabs:
- **About the Marshall Triangle** — conceptual overview
- **State & Calibration** — sliders and white point calibration
- **Visualization Settings** — rendering parameter controls and presets

The labeled diagram view uses `plot_with_labels()` which annotates all six named points (three midpoints and three vertices). The unlabeled view uses `st.image()` directly for faster rendering.

---

## 3. Rendering Engine (HarmonyIndex)

### 3.1 Geometric Layout

The triangle is defined as an equilateral triangle scaled to fit within a unit square (scale factor 0.95 to avoid corner clipping):

```
Top vertex:          (0,    +h/2 · s)
Bottom-left vertex:  (-s,   -h/2 · s)
Bottom-right vertex: (+s,   -h/2 · s)

where h = √3, s = 0.95
```

Color sources are placed at edge midpoints:

| Source | Position | Channel |
|--------|----------|---------|
| Red (Privacy) | Midpoint of top–bottom-left edge | R |
| Green (Performance) | Midpoint of top–bottom-right edge | G |
| Blue (Personalization) | Midpoint of bottom-left–bottom-right edge | B |

Secondary colors emerge at the vertices through additive mixing:
- Top vertex (Yellow) — equidistant from Red and Green
- Bottom-left vertex (Magenta) — equidistant from Red and Blue
- Bottom-right vertex (Cyan) — equidistant from Green and Blue
- Center (White) — equidistant from all three when state vector is balanced

### 3.2 Gaussian Falloff

For each pixel at coordinate `(x, y)`, the contribution from a midpoint source at `(cx, cy)` is:

```
w(x, y) = intensity · exp(−d² / 2σ_eff²)

where d² = (x−cx)² + (y−cy)²
      σ_eff = σ · 1.8
```

The effective sigma (`σ · 1.8`) widens the Gaussian to produce overlap at the triangle center, which is necessary for the white equilibrium point to appear.

The falloff is summed across all three sources with per-channel state weighting (see Section 3.3), then normalized so the maximum value across R, G, B at each pixel is at most 1.0:

```
R_norm = R / max(R, G, B)   (where max > threshold)
G_norm = G / max(R, G, B)
B_norm = B / max(R, G, B)
```

This max-value normalization preserves hue while preventing RGB clipping, ensuring all colors remain vivid regardless of intensity.

An alternative `inverse_square` falloff is also available:

```
w(x, y) = intensity · 0.8 / (d² + 0.05)
```

The `+0.05` offset prevents the singularity at the source point.

### 3.3 State Vector and Calibration

The **state vector** `{r, g, b}` ∈ [0, 1]³ weights each color channel's contribution. Before applying weights, the vector is normalized against the **calibrated white point** `{wr, wg, wb}`:

```
r_scaled = r · (max(wr, wg, wb) / wr)
g_scaled = g · (max(wr, wg, wb) / wg)
b_scaled = b · (max(wr, wg, wb) / wb)
```

This transformation ensures that when `{r, g, b} = {wr, wg, wb}` (the user's chosen balance point), the scaled values are equal, producing the white equilibrium regardless of the absolute values chosen.

### 3.4 Adaptive Sigma

When the state vector is strongly imbalanced, a single dominant color can flood the triangle and obscure gradient structure. The adaptive sigma system detects this and expands the Gaussian to maintain visual coherence.

**Imbalance score** — normalized standard deviation of the channel proportions:

```
p_i = channel_i / (r + g + b)
mean = 1/3
imbalance = std(p_r, p_g, p_b) / 0.471
```

`0.471` is the theoretical maximum standard deviation (one channel at 1.0, others at 0).

**Sigma compensation** — when `imbalance > 0.20`:

```
factor = (imbalance − 0.20) / 0.80
σ_required = 0.35 + (0.48 − 0.35) · factor
σ_effective = max(σ_base, σ_required)
```

The UI displays a warning when compensation is active, showing both the base and effective sigma values.

### 3.5 Edge Treatment

After the pixel grid is computed, a `scipy.ndimage.binary_dilation` pass identifies the one-pixel border of the triangle mask. Pixels on this border have their RGB values multiplied by `edge_factor` (default 0.5) to create a soft boundary. A final `PIL.ImageFilter.GaussianBlur` with radius `edge_blur` (default 0.5) is applied to the entire image.

---

## 4. Dependency Management

### 4.1 Package Manager

The project uses `uv` for Python dependency management. `pyproject.toml` declares constraints; `uv.lock` pins the exact resolved versions for reproducible installs.

### 4.2 Security Patch History

The following vulnerabilities were identified and remediated through sequential security scans during the buildout phase (May 2026):

**Batch 1 — May 2026:**

| Package | Before | After | Vulnerability |
|---------|--------|-------|--------------|
| pillow | 12.1.1 | 12.2.0 | Security fix |
| tornado | 6.5.4 | 6.5.5 | Security fix |

**Batch 2 — May 2026:**

| Package | Before | After | Vulnerability |
|---------|--------|-------|--------------|
| fonttools | 4.56.0 | 4.63.0 | GHSA-768j-98cg-p3fv |
| requests | 2.32.3 | 2.34.2 | GHSA-9hjg-9r4m-mvj7, GHSA-gc5v-m9x4-r6x2 |
| streamlit | 1.52.2 | 1.57.0 | GHSA-7p48-42j8-8846 |

**Batch 3 — May 2026:**

| Package | Before | After | Vulnerability |
|---------|--------|-------|--------------|
| gitpython | 3.1.44 | 3.1.50 | GHSA-7545, GHSA-mv93, GHSA-rpm5, GHSA-v87r, GHSA-x2qx (5× High) |
| urllib3 | 2.6.3 | 2.7.0 | PYSEC-2026-142, PYSEC-2026-141, GHSA-qccp (2× High, 2× Medium) |
| pyarrow | 19.0.1 | 24.0.0 | PYSEC-2026-113 (High) |
| idna | 3.10 | 3.16 | GHSA-65pc (Medium) |

All remediations involved raising minimum version constraints in `pyproject.toml` and re-running `uv lock` to regenerate the lockfile. No application logic was changed.

### 4.3 Post-Merge Automation

`scripts/post-merge.sh` runs `uv sync` automatically after any dependency task is merged via the Replit task system. This ensures the running environment stays in sync with the lockfile without manual intervention.

---

## 5. Deployment

### 5.1 Platform

The application runs on Replit Autoscale, deployed as a single workflow (`Stealth Mode`) that executes `python stealth_server.py`. The stealth server in turn spawns the Streamlit subprocess, so a single process command starts the full stack.

### 5.2 Workflow

| Workflow | Command | Port | Type |
|----------|---------|------|------|
| Stealth Mode | `python stealth_server.py` | 5000 | webview |

### 5.3 Statelessness

The application is fully stateless. No database is provisioned. Session state is ephemeral per Streamlit session. Rendered images are generated on demand and available for download but not persisted server-side.

---

## 6. Intellectual Property

| Asset | Details |
|-------|---------|
| **Source code** | MIT License — open implementation |
| **Visual outputs** | CC BY-NC 4.0 — attribution required, no commercial use |
| **Conceptual framework** | All Rights Reserved — Marshall Triangle concept, sovereign perceptual geometry, triadic calibration methodology |
| **On-chain IP registration** | Story Protocol asset `marshall_triangle-v1-sovereign` |
| **Story Protocol Explorer** | [0x8eE1e758dafc5Cb0Ee6D862D26eAF68eE33cf920](https://explorer.story.foundation/ipa/0x8eE1e758dafc5Cb0Ee6D862D26eAF68eE33cf920) |
| **Rights holder** | Fidelitas LLC |
| **Registration date** | December 28, 2025 |

---

## 7. Citation

> Marshall, P.W. (2026). *Marshall Triangle: A Geometric Framework for Triadic Balance Visualization*. Fidelitas LLC.

---

© 2026 Paul W. Marshall
© 2026 Fidelitas LLC. All rights reserved.
