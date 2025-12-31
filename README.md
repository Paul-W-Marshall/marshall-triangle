
# Harmony Triangle

A novel geometric visualization framework for representing triadic balance in complex systems.

## Overview

The Harmony Triangle introduces a unique approach to visualizing three-way relationships through color theory and geometric mathematics. Unlike traditional models that place primary elements at vertices, the Harmony Triangle positions them at edge midpoints, creating emergent secondary relationships at vertices and achieving perfect balance at the geometric center.

## Key Features

### Visual Framework
- **Midpoint Primaries**: Core elements positioned at triangle edge midpoints
- **Emergent Secondaries**: Natural combinations appear at vertices  
- **Harmonic Center**: Pure balance manifests as white light at geometric center
- **Dynamic Weighting**: Real-time adjustment of element influences

### Technical Implementation
- **Web App** (`/web`): Production-ready Next.js application with WebGL rendering
- **Figure Generation** (`/figures`): Computational tools for research and analysis
- **Shared Configuration** (`/config`): Color space definitions and anchor points

## Quick Start

### Web Application
```bash
cd web
npm install
npm run dev
```

### Figure Generation
```bash
cd figures  
npm install
npm run fig:f3  # Generate Figure 3
npm run fig:f4  # Generate Figure 4
```

## Applications

The Harmony Triangle framework has been applied to visualize:
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
- **Gaussian/Inverse-Square Falloff**: Distance-based influence calculations
- **Additive Blending**: Natural color combination at intersection points

## Directory Structure

```
harmony-triangle/
├── web/                    # Next.js web application
├── figures/               # Figure generation tools
├── config/                # Shared configuration files
├── .github/workflows/     # CI/CD automation
└── docs/                  # Documentation and research
```

## Deployment

The web application is optimized for deployment on modern platforms:
- **Vercel**: Set root directory to `/web`
- **Netlify**: Configure build directory as `/web`
- **Replit**: Direct deployment support

## Research Context

This work extends traditional color theory and geometric visualization concepts, drawing inspiration from:
- Maxwell's Triangle (color theory)
- Barycentric coordinate systems (computational geometry)
- Additive color synthesis (digital graphics)

## License

- **Web Application**: MIT License (see `LICENSE-MIT`)
- **Research Materials**: Creative Commons BY 4.0 (see `LICENSE-CC-BY-4.0`)
- **Educational Content**: Creative Commons BY-NC 4.0 (see `LICENSE-CC-BY-NC-4.0`)

## Citation

If you use this work in academic research, please cite:

```
Marshall, P.W. (2024). Harmony Triangle: A Geometric Framework for 
Triadic Balance Visualization. https://github.com/Paul-W-Marshall/harmony-triangle
```

## Contributing

Contributions welcome! Please see individual component README files for specific development guidelines.

---

*The Harmony Triangle project represents ongoing research into geometric visualization of complex multi-dimensional relationships.*
