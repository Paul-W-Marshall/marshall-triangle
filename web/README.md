
# Harmony Triangle Web App

Production-ready Next.js 14 TypeScript application for the Marshall Triangle visualization.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Development

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **API**: Next.js API routes

## API Endpoints

- `GET /api/health` - Health check endpoint
- `GET /api/color?x=&y=&mode=srgb|p3` - Color calculation endpoint

## Deployment on Vercel

1. Connect your GitHub repository to Vercel
2. Set the **Root Directory** to `web`
3. Vercel will automatically detect Next.js and use the correct build settings
4. Deploy!

The build configuration is already set up in `vercel.json`.

## Project Structure

```
web/
├── app/                 # Next.js App Router
│   ├── api/            # API routes
│   ├── globals.css     # Global styles
│   ├── layout.tsx      # Root layout
│   └── page.tsx        # Home page
├── components/         # React components
├── lib/               # Utility functions
│   ├── math/          # Mathematical calculations
│   └── color/         # Color space conversions
├── public/            # Static assets
└── package.json       # Dependencies and scripts
```

## Environment

- Node.js 20+
- npm or yarn

## License

MIT License - see LICENSE-MIT file for details.
