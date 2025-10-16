# AIMS Readiness - Frontend

Next.js 14 frontend for ISO/IEC 42001 + EU AI Act compliance platform.

## Features

- Dashboard with KPIs and readiness metrics
- AI systems inventory with CSV import
- System detail views with tabbed interface
- AI Act classification and gap analysis
- Evidence upload with file management
- Report generation and templates

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui components

## Setup

### Prerequisites

- Node.js 18+
- npm or pnpm

### Installation

```bash
# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with your API URL
```

### Development

```bash
# Run dev server
npm run dev

# App available at:
# http://localhost:3000
```

### Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://127.0.0.1:8000)

## Authentication

Currently uses API key authentication stored in localStorage. 

⚠️ **Development Only**: This approach is not secure for production. OAuth will be added in future versions.

## Pages

- `/` - Dashboard overview
- `/login` - API key authentication
- `/inventory` - AI systems list with import
- `/systems/[id]` - System details with tabs
- `/reports` - Export and templates

## API Integration

All API calls go through `/lib/api.ts` which:
- Adds X-API-Key header from localStorage
- Handles errors consistently
- Provides typed API methods

## Components

UI components are based on shadcn/ui and located in `/components/ui/`.

To add more components, visit: https://ui.shadcn.com/

