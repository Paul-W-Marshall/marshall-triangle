# Marshall Triangle — Technical Overview

**Author:** Paul W. Marshall  
**Entity:** Fidelitas LLC  
**Date:** June 2026  
**Version:** 1.0

---

## 1. Project Purpose

Marshall Triangle is a geometric visualization framework for representing triadic balance in complex systems. It maps three competing concerns — Privacy, Performance, and Personalization — to color sources at the midpoints of an equilateral triangle and renders their interaction using radial Gaussian falloff. The result is a continuously graded color field that communicates the relative weight of each concern at a glance.

The framework is publicly accessible at:

- **[marshalltriangle.app](https://marshalltriangle.app)** — Interactive application
- **[marshalltriangle.com](https://marshalltriangle.com)** — Explanatory and documentary landing site

---

## 2. High-Level Architecture

The system is composed of three layers:

| Layer | Role |
|-------|------|
| **Access Layer** | Tornado async HTTP server — handles the public endpoint and routes traffic to the application |
| **Application Layer** | Streamlit web application — the interactive Marshall Triangle interface |
| **Rendering Engine** | HarmonyIndex — pure Python/NumPy Gaussian rendering pipeline |

The application is fully stateless. No database is provisioned. All session state is ephemeral and scoped to a single browser session.

### 2.1 Deployment

The application runs on Replit, deployed as a single process that starts both the HTTP server and the Streamlit subprocess. Dependencies are managed with `uv` and pinned via `uv.lock` for reproducible installs.

| Domain | Role |
|--------|------|
| [marshalltriangle.app](https://marshalltriangle.app) | Interactive application |
| [marshalltriangle.com](https://marshalltriangle.com) | Static explanatory and documentary landing site |
| [github.com/Paul-W-Marshall/marshall-triangle](https://github.com/Paul-W-Marshall/marshall-triangle) | Canonical source repository |

---

## 3. Rendering Model

### 3.1 Geometric Layout

The triangle is an equilateral triangle scaled to fit within a unit square. Three color sources are placed at edge midpoints:

| Source | Channel | Triangle Position |
|--------|---------|-------------------|
| Privacy | Red | Midpoint of top–bottom-left edge |
| Performance | Green | Midpoint of top–bottom-right edge |
| Personalization | Blue | Midpoint of bottom-left–bottom-right edge |

Secondary colors emerge at the vertices through additive mixing:
- **Top vertex** — Yellow (Red + Green)
- **Bottom-left vertex** — Magenta (Red + Blue)
- **Bottom-right vertex** — Cyan (Green + Blue)
- **Center** — White (all three balanced)

### 3.2 Gaussian Falloff

For each pixel at coordinate `(x, y)`, the contribution from a midpoint source at `(cx, cy)` is:

```
w(x, y) = intensity · exp(−d² / 2σ_eff²)

where d² = (x−cx)² + (y−cy)²
      σ_eff = σ · 1.8
```

The effective sigma (`σ · 1.8`) widens the Gaussian to produce overlap at the triangle center, which is necessary for the white equilibrium point to emerge.

Contributions across all three sources are summed with per-channel state weighting and normalized so the maximum RGB value at each pixel is at most 1.0, preserving hue while preventing clipping.

### 3.3 Key Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Canonical sigma | 0.30 | Optimal color blending |
| Valid sigma range | 0.1 – 0.6 | User-adjustable |
| Default intensity | 1.2 | Gaussian amplitude multiplier |
| Default size | 500 px | Render resolution |
| Color model | Additive RGB | Max-value normalization |

### 3.4 Adaptive Sigma

When the state vector is strongly imbalanced, sigma is automatically raised to maintain visual coherence.

**Imbalance score** — normalized standard deviation of the channel proportions:

```
p_i = channel_i / (r + g + b)
imbalance = std(p_r, p_g, p_b) / 0.471
```

**Sigma compensation** — when `imbalance > 0.20`:

```
factor = (imbalance − 0.20) / 0.80
σ_required = 0.35 + (0.48 − 0.35) · factor
σ_effective = max(σ_base, σ_required)
```

### 3.5 State Vector and Calibration

The **state vector** `{r, g, b}` ∈ [0, 1]³ weights each color channel's contribution. Users can define a custom **white point of harmony** — any RGB combination that should render as balanced. The calibration algorithm scales channels by `max / calibrated_value` so that the chosen point produces the white equilibrium in the rendered output.

### 3.6 Edge Treatment

After the pixel grid is computed, edge pixels at the triangle boundary are dimmed by an `edge_factor` (default 0.5) and a final `GaussianBlur` with radius `edge_blur` (default 0.5) is applied to the full image for smooth boundary rendering.

---

## 4. Public Links

| Resource | URL |
|----------|-----|
| Interactive App | [marshalltriangle.app](https://marshalltriangle.app) |
| Landing & Docs Site | [marshalltriangle.com](https://marshalltriangle.com) |
| GitHub Repository | [github.com/Paul-W-Marshall/marshall-triangle](https://github.com/Paul-W-Marshall/marshall-triangle) |
| Story Protocol IP | [View on Story Explorer](https://explorer.story.foundation/ipa/0x8eE1e758dafc5Cb0Ee6D862D26eAF68eE33cf920) |

---

## 5. Licensing

This project uses a tri-layer licensing model:

| Component | License | Scope |
|-----------|---------|-------|
| Source code | MIT | All `.py` files — open for reuse and modification |
| Visual outputs | CC BY-NC 4.0 | Generated triangle images and PNG exports |
| Conceptual framework | All Rights Reserved | Marshall Triangle concept, sovereign perceptual geometry, triadic calibration methodology |

The conceptual framework is registered as an on-chain IP asset via Story Protocol (`marshall_triangle-v1-sovereign`, rights holder: Fidelitas LLC, registered December 28, 2025).

---

## 6. Archive & Preprint Roadmap

| Channel | Status |
|---------|--------|
| GitHub release | Forthcoming |
| Zenodo DOI | Forthcoming (will archive the GitHub release) |
| Preprints.org | Resubmission planned |

---

## 7. Citation

> Marshall, P.W. (2026). *Marshall Triangle: A Geometric Framework for Triadic Balance Visualization*. Fidelitas LLC.  
> Available: [marshalltriangle.app](https://marshalltriangle.app)

---

© 2026 Paul W. Marshall  
© 2026 Fidelitas LLC. All rights reserved.
