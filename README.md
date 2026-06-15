# Marshall Triangle

A novel geometric visualization framework for representing triadic balance in complex systems through color theory and radial coordinate geometry.

## Canonical Naming

- **Public name**: Marshall Triangle
- **Internal class**: HarmonyIndex (rendering engine)
- **Pattern**: Semantic Governance Kit v1 — Technical / Tool Pattern

## Links

| Resource | URL |
|----------|-----|
| **Interactive App** | [marshalltriangle.app](https://marshalltriangle.app) |
| **Landing & Docs Site** | [marshalltriangle.com](https://marshalltriangle.com) |
| **GitHub Repository** | [github.com/Paul-W-Marshall/marshall-triangle](https://github.com/Paul-W-Marshall/marshall-triangle) |
| **Story Protocol IP** | [View on Story Explorer](https://explorer.story.foundation/ipa/0x8eE1e758dafc5Cb0Ee6D862D26eAF68eE33cf920) |
| **Preprint / Archive** | GitHub release and Zenodo DOI forthcoming; Preprints.org resubmission planned. |

## Overview

The Marshall Triangle positions three competing concerns as **midpoint sources** along the edges of an equilateral triangle:

- **Privacy (Red)** — User data protection and anonymity
- **Performance (Green)** — System speed and efficiency
- **Personalization (Blue)** — Tailored user experiences

Secondary colors (Yellow, Cyan, Magenta) emerge at the triangle **vertices** through additive color mixing, while the **convergent white equilibrium point** manifests at the geometric center when all three concerns are balanced.

### Rendering Model

The rendering engine uses **radial Gaussian falloff** from three midpoint sources—not barycentric interpolation. Each pixel's color is computed as the additive sum of distance-weighted contributions from Privacy (Red), Performance (Green), and Personalization (Blue) sources.

Key characteristics:
- **Falloff function**: Gaussian (`exp(-dist² / 2σ²)`)
- **Canonical sigma**: 0.30 (optimal for balanced color blending)
- **Color mixing**: Additive RGB weighted by distance and state vector
- **Normalization**: Max-value normalization prevents clipping

## Architecture

| Layer | Description | Status |
|-------|-------------|--------|
| **Stealth Gate** | Tornado proxy — serves curtain to public, routes authorized users to app | Active |
| **Interactive App** | Streamlit on Replit (internal port 8501) — live at [marshalltriangle.app](https://marshalltriangle.app) | Active |
| **Landing & Docs Site** | Static explanatory and documentary surface — [marshalltriangle.com](https://marshalltriangle.com) | Active |
| **GitHub Repo** | Canonical technical source | Active |

### Access Control

The app is currently in **stealth mode**. The public URL displays a holding page. Authorized users bypass it via a secret link:

```
https://your-app.replit.app/?key=BYPASS_KEY
```

The first visit sets a secure cookie (7-day expiry). Subsequent visits are recognized automatically. The key is stored as an environment secret and can be rotated at any time.

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | Streamlit application entry point and UI |
| `harmony_index.py` | HarmonyIndex rendering engine |
| `stealth_server.py` | Tornado-based stealth gate and proxy |
| `index.html` | Public-facing stealth curtain page |
| `scripts/post-merge.sh` | Dependency sync script run after dependency updates |
| `pyproject.toml` | Python project manifest and dependency constraints |
| `uv.lock` | Locked dependency tree for reproducible installs |

## Licensing & Attribution

This project uses a **tri-layer licensing model**:

| Component | License | Scope |
|-----------|---------|-------|
| **Source Code** | MIT License | `app.py`, `harmony_index.py`, all `.py` files |
| **Visual Outputs** | CC BY-NC 4.0 | Generated triangle images, PNG exports, screenshots |
| **Conceptual Framework** | All Rights Reserved | Marshall Triangle concept, sovereign perceptual geometry, triadic calibration methodology |

### License Files

- [`LICENSE-MIT`](./LICENSE-MIT) — Open-source code license
- [`LICENSE-CC-BY-NC-4.0`](./LICENSE-CC-BY-NC-4.0) — Figure/visual attribution license

### Intellectual Property

The conceptual framework is registered via **Story Protocol** as an on-chain IP asset.

| Property | Value |
|----------|-------|
| **IP Asset** | `marshall_triangle-v1-sovereign` |
| **Story Protocol Explorer** | [View IP Details](https://explorer.story.foundation/ipa/0x8eE1e758dafc5Cb0Ee6D862D26eAF68eE33cf920) |
| **Rights Holder** | Fidelitas LLC |
| **Registered** | December 28, 2025 |

The MIT license applies **only** to the implementation code. Use of the Marshall Triangle concept, methodology, or sovereign perceptual geometry framework requires separate authorization.

### Citation

If referencing this work in academic or commercial contexts:

> Marshall, P.W. (2026). *Marshall Triangle: A Geometric Framework for Triadic Balance Visualization*. Fidelitas LLC.

## Technical Details

### Rendering Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Canonical sigma** | 0.30 | Optimal Gaussian falloff |
| **Valid range** | 0.1 – 0.6 | User-adjustable |
| **Adaptive sigma** | Auto-compensates when imbalance > 20% | Maintains visual coherence |
| **Default intensity** | 1.2 | Gaussian amplitude multiplier |
| **Default size** | 500 px | Render resolution |

### Triadic Calibration

Users can define a custom **white point of harmony** where any RGB combination renders as balanced. The calibration algorithm scales channels by `max / calibrated_value` to normalize the visual output. Calibration is session-scoped and resets on page reload.

### Adaptive Sigma

When the imbalance score of the state vector exceeds 20% (measured as normalized standard deviation across the three channels), sigma is automatically raised toward a maximum of 0.48 to preserve visual coherence. The compensation threshold and range are:

- Threshold: imbalance > 0.20
- Minimum compensated sigma: 0.35
- Maximum sigma: 0.48

## Copyright

© 2026 Paul W. Marshall
© 2026 Fidelitas LLC. All rights reserved.

---

*This repository is the canonical reference implementation of the Marshall Triangle visualization framework.*
