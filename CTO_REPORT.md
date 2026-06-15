# Marshall Triangle — CTO Report

**Prepared by:** Paul W. Marshall  
**Entity:** Fidelitas LLC  
**Date:** June 15, 2026  
**Classification:** Internal / Governance  

---

## 1. Executive Summary

Marshall Triangle is production-live. The interactive application is accessible at **[marshalltriangle.app](https://marshalltriangle.app)** and the explanatory landing site at **[marshalltriangle.com](https://marshalltriangle.com)**. The system is stateless, gated, and fully deployed on Replit Reserved VM.

Three rounds of dependency security remediation have been completed. All known CVEs are resolved. The conceptual framework is protected under a provisional U.S. patent and registered as an on-chain IP asset via Story Protocol. A three-layer licensing model (MIT / CC BY-NC 4.0 / All Rights Reserved) governs use by domain.

The codebase is in a stable, maintainable state. Two deferred enhancements are tracked as open items.

---

## 2. System Architecture

### 2.1 Overview

```
Public Internet
      │
      ▼
┌──────────────────────────────┐
│  Tornado Stealth Gate        │  :5000 (public)
│  stealth_server.py           │
│  ── cookie / key auth        │
│  ── HTTP + WebSocket proxy   │
└─────────────┬────────────────┘
              │  authorized traffic only
              ▼
┌──────────────────────────────┐
│  Streamlit Application       │  :8501 (internal)
│  app.py                      │
│  ── UI / session state       │
│  ── HarmonyIndex calls       │
└─────────────┬────────────────┘
              │
              ▼
┌──────────────────────────────┐
│  HarmonyIndex Engine         │
│  harmony_index.py            │
│  ── Gaussian rendering       │
│  ── Triadic Calibration      │
│  ── Adaptive Sigma           │
└──────────────────────────────┘
```

### 2.2 Live Endpoints

| Domain | Role | Status |
|--------|------|--------|
| [marshalltriangle.app](https://marshalltriangle.app) | Interactive application (Tornado → Streamlit) | Live |
| [marshalltriangle.com](https://marshalltriangle.com) | Explanatory and documentary landing site | Live |
| [github.com/Paul-W-Marshall/marshall-triangle](https://github.com/Paul-W-Marshall/marshall-triangle) | Canonical source repository | Active |

### 2.3 Platform

| Property | Value |
|----------|-------|
| **Host** | Replit Reserved VM |
| **Run command** | `uv run python stealth_server.py` |
| **Public port** | 5000 (Tornado gate) |
| **Internal port** | 8501 (Streamlit, not exposed) |
| **State** | Fully stateless — no database, session-scoped only |
| **Package manager** | `uv` with locked `uv.lock` (reproducible installs) |

---

## 3. Access Control

The app operates in **stealth mode**. The public URL renders a holding page (`index.html`) to unauthorized visitors. Authorized access is granted via a secret bypass link that sets a signed 7-day cookie.

| Property | Detail |
|----------|--------|
| **Auth mechanism** | HMAC-signed cookie (`stealth_bypass`) |
| **Key storage** | Replit environment secret (`BYPASS_KEY`) — never in source |
| **Cookie expiry** | 7 days |
| **Key rotation** | Immediate invalidation — rotate by updating the secret |
| **WebSocket proxy** | Bidirectional; required for Streamlit's `/_stcore/stream` |

---

## 4. Security Posture

### 4.1 Dependency Vulnerability Remediation

All known CVEs resolved across three remediation batches (May 2026):

| Batch | Packages Patched | Severity |
|-------|-----------------|----------|
| 1 | pillow 12.1.1 → 12.2.0, tornado 6.5.4 → 6.5.5 | Security fixes |
| 2 | fonttools, requests, streamlit (1.52.2 → 1.57.0) | High |
| 3 | gitpython, urllib3, pyarrow, idna | High / Medium |

Current pinned versions with no known outstanding CVEs.

### 4.2 Application-Level Protections

| Control | Implementation |
|---------|---------------|
| **Download gate** | Code-required download (`^magicword\d{2}$` pattern); session-persisted unlock |
| **Image protection** | `pointer-events:none`, transparent CSS overlay on rendered images and plots |
| **Secret management** | All secrets via Replit environment — never committed |
| **Streamlit CSRF/CORS** | Disabled on internal-only port 8501 (not reachable from internet) |

### 4.3 Open Security Items

- Automated dependency health check scheduled (tracking — not yet implemented)
- No rate limiting on the stealth bypass endpoint (low risk; key is not publicly known)

---

## 5. Intellectual Property & Licensing

### 5.1 Three-Layer Licensing Model

| Layer | License | Scope |
|-------|---------|-------|
| Source code | MIT | All `.py` files — open for reuse and modification |
| Visual outputs | CC BY-NC 4.0 | Generated triangle images and PNG exports |
| Conceptual framework | All Rights Reserved | Marshall Triangle concept, sovereign perceptual geometry, triadic calibration methodology |

### 5.2 Patent & On-Chain Registration

| Asset | Detail |
|-------|--------|
| **U.S. Provisional Patent** | U.S. Prov. App. No. 63/841,753 (Pending) — Fidelitas LLC Patent Portfolio |
| **Story Protocol IP asset** | `marshall_triangle-v1-sovereign` |
| **Story Explorer** | [0x8eE1e758dafc5Cb0Ee6D862D26eAF68eE33cf920](https://explorer.story.foundation/ipa/0x8eE1e758dafc5Cb0Ee6D862D26eAF68eE33cf920) |
| **Rights holder** | Fidelitas LLC |
| **Registration date** | December 28, 2025 |

### 5.3 Archive & Preprint Status

| Channel | Status |
|---------|--------|
| GitHub release | Forthcoming |
| Zenodo DOI | Forthcoming (will archive the GitHub release) |
| Preprints.org | Resubmission planned |

---

## 6. Core Technology

### 6.1 Rendering Engine (HarmonyIndex)

The rendering engine uses **radial Gaussian falloff** from three midpoint color sources — not barycentric interpolation. This produces smooth, physically plausible gradients with an emergent white equilibrium at the center when the state vector is balanced.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Canonical sigma | 0.30 | Optimal color blending |
| Adaptive sigma range | 0.35 – 0.48 | Auto-compensates when imbalance > 20% |
| Default intensity | 1.2 | Gaussian amplitude |
| Effective sigma multiplier | 1.8× | Ensures center overlap |
| Color model | Additive RGB | Max-value normalization prevents clipping |

### 6.2 Key Dependencies

| Package | Pinned Version | Role |
|---------|---------------|------|
| streamlit | 1.57.0 | Web application framework |
| tornado | ~6.5 | Async HTTP/WebSocket proxy |
| numpy | ~2.2 | Numerical rendering |
| scipy | ~1.15 | Edge dilation |
| pillow | 12.2.0 | Image processing / PNG export |
| matplotlib | ~3.10 | Labeled diagram output |
| pyarrow | ~24.0 | Streamlit data transport |

---

## 7. Operations

### 7.1 Deployment Workflow

```
git push → Replit merges → post-merge.sh runs uv sync → workflow restarts
```

`scripts/post-merge.sh` runs `uv sync` automatically after any dependency task merge. No manual environment setup required.

### 7.2 Session State (Ephemeral)

All user data is scoped to a single Streamlit session. State variables include the privacy/performance/personalization vector, sigma, calibration white point, named saved states, and rendering presets. Nothing is persisted server-side.

---

## 8. Open Items

| Item | Priority | Notes |
|------|----------|-------|
| In-app Light/Dark theme toggle | Medium | Tracked; allows theme switching without opening the menu |
| Automated dependency health check (scheduled) | Medium | Script exists; scheduling not yet wired |
| Zenodo DOI / GitHub release | Medium | Preprint archival pipeline |
| Preprints.org resubmission | Low | Planned |

---

## 9. Citation

> Marshall, P.W. (2026). *Marshall Triangle: A Geometric Framework for Triadic Balance Visualization*. Fidelitas LLC.  
> Available: [marshalltriangle.app](https://marshalltriangle.app)

---

© 2026 Paul W. Marshall  
© 2026 Fidelitas LLC. All rights reserved.
