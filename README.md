
# Marshall Triangle

A novel geometric visualization framework for representing triadic balance in complex systems.

[![Vercel](https://img.shields.io/badge/Deployed-Vercel-black)](https://vercel.com)
[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE-MIT)
[![License: CC BY 4.0](https://img.shields.io/badge/Paper-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/Figures-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

## Overview

The Marshall Triangle introduces a unique approach to visualizing three-way relationships through color theory and geometric mathematics. Unlike traditional models that place primary elements at vertices, the Marshall Triangle positions them at edge midpoints, creating emergent secondary relationships at vertices and achieving perfect balance at the geometric center.

## Key Features

### Visual Framework
- **Midpoint Primaries**: Core elements positioned at triangle edge midpoints
- **Emergent Secondaries**: Natural combinations appear at vertices  
- **Harmonic Center**: Pure balance manifests as white light at geometric center
- **Dynamic Weighting**: Real-time adjustment of element influences

### Technical Implementation
- **Web App** (`/web`): Production-ready Next.js application with WebGL rendering
- **Streamlit App** (`/apps/marshall-triangle/streamlit`): Python-based figure generation and research tool
- **Shared Configuration** (`/config`): Color space definitions and anchor points

## Quick Start

### Web Application
```bash
cd web
npm install
npm run dev
```

### Streamlit Application
```bash
cd apps/marshall-triangle/streamlit
streamlit run app.py --server.port 5000
```

## Applications

The Marshall Triangle framework has been applied to visualize:
- **Privacy-Performance-Personalization** trade-offs in technology systems
- **Quality-Speed-Cost** relationships in project management
- **Theory-Practice-Innovation** dynamics in research contexts

## Technical Architecture

### Color Spaces
- **sRGB**: Standard web-compatible color representation
- **Display P3**: Extended gamut for modern displays
- **Configurable Anchors**: Customizable primary and vertex coordinates

### Mathematical Foundation
- **Barycentric Coordinates**: Precise positional mapping within triangle
- **Gaussian/Inverse-Square Falloff**: Distance-based influence calculations (canonical σ = 0.25)
- **Additive Blending**: Natural color combination at intersection points

## Directory Structure

```
marshall-triangle/
├── apps/
│   └── marshall-triangle/
│       ├── streamlit/        # Python/Streamlit application
│       ├── web/              # Next.js web application (mirror)
│       ├── config/           # Shared configuration
│       ├── PIL_METADATA.yaml # Story Protocol IP metadata
│       └── LICENSE-PUBLIC.txt
├── web/                      # Next.js web application (primary)
├── config/                   # Color space configuration files
└── docs/                     # Documentation and research
```

## Deployment

The web application is optimized for deployment on modern platforms:
- **Vercel**: Set root directory to `/web`
- **Replit**: Direct deployment support via Streamlit

## Research Context

This work extends traditional color theory and geometric visualization concepts, drawing inspiration from:
- Maxwell's Triangle (color theory)
- Barycentric coordinate systems (computational geometry)
- Additive color synthesis (digital graphics)

## License

This project uses a tiered licensing structure:

| Component | License | File |
|-----------|---------|------|
| **Source Code** | MIT | `LICENSE-MIT` |
| **Academic Paper** | CC BY 4.0 | See paper repository |
| **Generated Figures** | CC BY-NC 4.0 | `apps/marshall-triangle/LICENSE-PUBLIC.txt` |

**Note:** AI training use requires explicit permission. See `apps/marshall-triangle/PIL_METADATA.yaml` for Story Protocol integration details.

## Citation

If you use this work in academic research, please cite:

```
Marshall, P.W. (2024). Marshall Triangle: A Geometric Framework for 
Triadic Balance Visualization. https://github.com/Paul-W-Marshall/marshall-triangle
```

## Contributing

Contributions welcome! Please see individual component README files for specific development guidelines.

---

*The Marshall Triangle project represents ongoing research into geometric visualization of complex multi-dimensional relationships.*
