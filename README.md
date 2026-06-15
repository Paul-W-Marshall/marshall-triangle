# Marshall Triangle

A geometric visualization framework for representing triadic balance in complex systems through color theory and radial coordinate geometry.

## Canonical Naming

- **Public name**: Marshall Triangle
- **Internal class**: HarmonyIndex (rendering engine)

## Links

| Resource | URL |
|----------|-----|
| **Interactive App** | [marshalltriangle.app](https://marshalltriangle.app) |
| **Landing & Docs Site** | [marshalltriangle.com](https://marshalltriangle.com) |
| **GitHub Repository** | [github.com/Paul-W-Marshall/marshall-triangle](https://github.com/Paul-W-Marshall/marshall-triangle) |
| **Story Protocol IP** | [View on Story Explorer](https://explorer.story.foundation/ipa/0x8eE1e758dafc5Cb0Ee6D862D26eAF68eE33cf920) |
| **Preprint / Archive** | [paper/Marshall_Triangle_Preprint_v1_1_1.pdf](./paper/Marshall_Triangle_Preprint_v1_1_1.pdf) · [doi.org/10.5281/zenodo.20696529](https://doi.org/10.5281/zenodo.20696529) |

## Overview

The Marshall Triangle positions three competing concerns as **midpoint sources** along the edges of an equilateral triangle:

- **Privacy (Red)** — User data protection and anonymity
- **Performance (Green)** — System speed and efficiency
- **Personalization (Blue)** — Tailored user experiences

Secondary colors (Yellow, Cyan, Magenta) emerge at the triangle **vertices** through additive color mixing, while the **convergent white equilibrium point** manifests at the geometric center when all three concerns are balanced.

### Rendering Model

The rendering engine uses **radial Gaussian falloff** from three midpoint sources — not barycentric interpolation. Each pixel's color is computed as the additive sum of distance-weighted contributions from Privacy (Red), Performance (Green), and Personalization (Blue) sources.

Key characteristics:
- **Falloff function**: Gaussian (`exp(-dist² / 2σ²)`)
- **Canonical sigma**: 0.30 (optimal for balanced color blending)
- **Color mixing**: Additive RGB weighted by distance and state vector
- **Normalization**: Max-value normalization prevents clipping

## Architecture

| Layer | Description | Status |
|-------|-------------|--------|
| **Access Layer** | Tornado async HTTP server — serves the public endpoint and routes traffic to the app | Active |
| **Interactive App** | Streamlit application — live at [marshalltriangle.app](https://marshalltriangle.app) | Active |
| **Landing & Docs Site** | Static explanatory and documentary surface — [marshalltriangle.com](https://marshalltriangle.com) | Active |
| **GitHub Repo** | Canonical technical source | Active |

The application is currently in a limited-access rollout phase. Public availability will be announced via the landing site.

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | Streamlit application entry point and UI |
| `harmony_index.py` | HarmonyIndex rendering engine |
| `stealth_server.py` | Tornado-based HTTP server and proxy |
| `index.html` | Public-facing holding page |
| `scripts/post-merge.sh` | Dependency sync script run after dependency updates |
| `pyproject.toml` | Python project manifest and dependency constraints |
| `uv.lock` | Locked dependency tree for reproducible installs |

## Paper / Archive

The revised preprint is included in this repository as the canonical archive source for the upcoming GitHub release and Zenodo DOI.

| File | Description |
|------|-------------|
| [`paper/Marshall_Triangle_Preprint_v1_1_1.pdf`](./paper/Marshall_Triangle_Preprint_v1_1_1.pdf) | Revised preprint — v1.1.1 |
| [`paper/Marshall_Triangle_Preprint_v1_1_1.tex`](./paper/Marshall_Triangle_Preprint_v1_1_1.tex) | LaTeX source |
| [`paper/Marshall_Triangle_Preprint_v1_1_1_LaTeX_Bundle.zip`](./paper/Marshall_Triangle_Preprint_v1_1_1_LaTeX_Bundle.zip) | Full LaTeX bundle (source + figures) |

This version reduces self-citation exposure, adds external scholarly references, and strengthens the mathematical formulation. It is prepared for:
- GitHub release (this repository)
- Zenodo DOI archive: [https://doi.org/10.5281/zenodo.20696529](https://doi.org/10.5281/zenodo.20696529)
- Later Preprints.org resubmission

**Figures** referenced in the paper are stored in [`figures/`](./figures/).

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
