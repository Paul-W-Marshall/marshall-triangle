# Harmony Triangle

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Vercel](https://vercelbadge.vercel.app/api/Paul-W-Marshall/harmony-triangle)](https://vercel.com/)
<!-- Add more badges as needed (e.g., arXiv, DOI, build status) -->

## Overview

**Harmony Triangle** is a reference implementation and interactive visualization of a novel color space design system, building on James Clerk Maxwell’s 1874 color triangle. This repository provides both a production-ready Next.js 14 + WebGL web app and a TypeScript toolchain for generating publication-quality figures.

Developed alongside the forthcoming arXiv paper, which details the theoretical and historical foundations of the Harmony Triangle.

---

## Features

- **Interactive barycentric triangle renderer**
- **sRGB / Display-P3 space toggle** (with live badge)
- **Draggable probe** showing barycentric weights, hex color, and copy-to-JSON
- **PNG export** (color-managed, space-aware)
- **TypeScript toolchain** (`/figures`) for generating publication-quality PNGs and CSV data
- **Shared color-math utilities** and JSON-configured anchors

---

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/Paul-W-Marshall/harmony-triangle.git
cd harmony-triangle/web
npm install
```

### 2. Run the Web App

```bash
npm run dev
```
Visit [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Generate Figures

```bash
cd ../figures
npm install
npm run build && npm run generate
```

---

## Deployment

This project is pre-configured for [Vercel](https://vercel.com/) deployment.

- **Root Directory:** `/web`
- **Build Command:** `npm run build`
- **Output Directory:** `.next`

---

## Provenance and Citations

- Public repository for reproducibility and scholarly citation.
- Full commit history preserved.
- Original private archival repository referenced in the paper's Appendix/Provenance section.
- Based on James Clerk Maxwell’s 1874 color triangle ([Maxwell, J.C., "On the Theory of Compound Colours," 1860](https://doi.org/10.1098/rstl.1860.0005)).
- Please cite the associated arXiv paper (link forthcoming).

<details>
<summary><strong>How to Cite</strong></summary>

When citing this project, please use the following format (update when arXiv DOI is available):

```
@software{marshall_harmonytriangle,
  author = {Paul Warrington Marshall},
  title = {Harmony Triangle: Reference Implementation and Visualization},
  year = {2024},
  url = {https://github.com/Paul-W-Marshall/harmony-triangle},
  note = {arXiv preprint forthcoming}
}
```
</details>

---

## License

- **Code:** [MIT](./LICENSE)
- **Paper:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Figures:** [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)

See LICENSE files in root and subdirectories for details.

---

## Contributing

Contributions are welcome! Please open an issue or pull request for suggestions, improvements, or bug reports.

---

## Contact

For questions or academic inquiries, please contact [Paul Warrington Marshall](https://github.com/Paul-W-Marshall) or open an issue in this repository.

---

## Acknowledgements

Credit to James Clerk Maxwell for the foundational work on color triangles.

---

<!--
Optionally, add screenshots or GIFs here, e.g.:

## Screenshots

![Screenshot of Harmony Triangle Web App](./web/public/screenshot.png)
-->
