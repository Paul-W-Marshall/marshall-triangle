# Marshall Triangle

A novel geometric visualization framework for representing triadic balance in complex systems through color theory and radial coordinate geometry.

## Canonical Naming

- **Public name**: Marshall Triangle
- **Internal class**: HarmonyIndex (rendering engine)
- **Pattern**: Semantic Governance Kit v1 — Technical / Tool Pattern

## Links

| Resource | URL |
|----------|-----|
| **Interactive App** | [Replit Deployment](https://985dc837-9240-474b-aa3c-ae5f1633b4a5-00-esqi2fvj78xf.riker.replit.dev) |
| **GitHub Repository** | [github.com/Paul-W-Marshall/marshall-triangle](https://github.com/Paul-W-Marshall/marshall-triangle) |
| **Story Protocol Mint** | `marshall_triangle-v1-sovereign` |
| **Preprint** | *(Coming soon — will be hosted on OSF/Zenodo/arXiv)* |

*Note: Custom domain `marshalltriangle.app` is planned but not yet configured.*

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
| **Interactive App** | Streamlit on Replit Autoscale | Active |
| **GitHub Repo** | Canonical technical source | Active |
| **Static Container** | marshalltriangle.com | Planned |

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
| **Minted Asset ID** | `marshall_triangle-v1-sovereign` |
| **Rights Holder** | Fidelitas LLC – Series 1 |
| **Year** | 2026 |

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

### Triadic Calibration

Users can define a custom **white point of harmony** where any RGB combination renders as balanced. The calibration algorithm scales channels by `max / calibrated_value` to normalize the visual output.

### Key Files

| File | Purpose |
|------|---------|
| `app.py` | Streamlit application entry point |
| `harmony_index.py` | HarmonyIndex rendering engine |
| `refresh_trigger.py` | State synchronization helper |
| `calibration.json` | User's white point calibration (runtime) |
| `harmony_presets.db` | SQLite database for saved states |

## Copyright

© 2026 Paul W. Marshall  
© 2026 Fidelitas LLC – Series 1

---

*This repository is the canonical reference implementation of the Marshall Triangle visualization framework.*
