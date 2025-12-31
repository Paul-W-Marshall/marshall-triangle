
# Developer Quickstart

## Prerequisites

- Node.js 20+ (check with `node --version`)
- npm or yarn

## Setup

```bash
# Navigate to web directory
cd web/

# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Development Workflow

1. **Components**: Add React components in `components/`
2. **API Routes**: Add API endpoints in `app/api/`
3. **Utilities**: Add helper functions in `lib/`
4. **Styling**: Use Tailwind CSS classes

## Key Commands

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build
```

## Testing the API

```bash
# Health check
curl http://localhost:3000/api/health

# Color endpoint
curl "http://localhost:3000/api/color?x=0.5&y=0.5&mode=srgb"
```

## File Structure

- `app/page.tsx` - Main landing page
- `components/TriangleCanvas.tsx` - Interactive canvas component
- `lib/math/barycentric.ts` - Mathematical calculations (stub)
- `lib/color/space.ts` - Color space conversions (stub)

## Next Steps

1. Implement real barycentric coordinate calculations
2. Add WebGL rendering for performance
3. Implement Display-P3 color space support
4. Add interactive controls
