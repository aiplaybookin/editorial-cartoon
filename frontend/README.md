# Arrakis Marketeer - Frontend

React + TypeScript frontend for the AI-powered email marketing platform.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **React Router v6** - Routing
- **TanStack Query (React Query)** - Server state management
- **Zustand** - Client state management
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **Axios** - HTTP client
- **React Hook Form** - Form handling
- **Zod** - Schema validation

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Update .env.local with your API URL if different
```

### Development

```bash
# Start development server
npm run dev

# Open browser to http://localhost:5173
```

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── api/              # API client & service functions
├── assets/           # Static assets (images, logos)
├── components/       # Reusable components
│   ├── ui/          # shadcn/ui components
│   ├── layout/      # Layout components
│   ├── auth/        # Auth-related components
│   ├── campaigns/   # Campaign components
│   ├── ai/          # AI generation components
│   └── common/      # Common components
├── hooks/           # Custom React hooks
├── layouts/         # Page layouts
├── pages/           # Route pages
├── store/           # Zustand stores
├── types/           # TypeScript types
├── utils/           # Utility functions
├── App.tsx          # Root component
├── router.tsx       # Route configuration
└── main.tsx         # Entry point
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Environment Variables

See `.env.example` for all available environment variables:

- `VITE_API_BASE_URL` - Backend API URL (default: http://localhost:8000)
- `VITE_APP_NAME` - Application name
- `VITE_ENABLE_ANALYTICS` - Enable analytics (true/false)

## Key Features

- ✅ JWT authentication with automatic token refresh
- ✅ Protected routes
- ✅ API client with interceptors
- ✅ Type-safe API calls
- ✅ React Query for caching & state management
- ✅ Zustand for auth & UI state
- ✅ Tailwind CSS + shadcn/ui components
- ✅ Form validation with Zod
- ✅ Toast notifications
- ✅ Responsive design

## Next Steps

Phase 2 will implement:
- Authentication pages (Login, Signup, Password Reset)
- Campaign management pages
- AI email generation interface
- Dashboard with statistics

## Contributing

See the main project README for contribution guidelines.
