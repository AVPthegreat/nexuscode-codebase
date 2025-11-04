# Codebase Judge System - Quick Start Guide

## Services Running

### Backend Services (Docker)
- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Judge Server**: Port 12358
- **PostgreSQL**: Port 5432
- **Redis**: Port 6379

### Frontend (Development)
- **Frontend Dev Server**: http://localhost:8080

## Start/Stop Commands

### Backend (Docker Compose)
```bash
# Start all backend services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f backend
docker compose logs -f judge-server

# Check service status
docker compose ps
```

### Frontend (Vue.js Dev Server)

**Option 1: Use the helper script (recommended)**
```bash
cd OnlineJudgeFE
./dev.sh
```

**Option 2: Run manually**
```bash
cd OnlineJudgeFE
NODE_OPTIONS=--openssl-legacy-provider TARGET=http://localhost:8000 npm run dev
```

The frontend will be available at http://localhost:8080 and will proxy API requests to the backend at http://localhost:8000.

## Recent Changes

### UI/UX Modifications
- ✅ Navbar is fixed (stays at top when scrolling)
- ✅ Changed logo from "OnlineJudge" to "codebase"

## Troubleshooting

### Frontend won't start
- Make sure Node.js v14+ is installed
- If you see OpenSSL errors with Node.js v17+, use the `NODE_OPTIONS=--openssl-legacy-provider` flag (already included in dev.sh)

### Backend connection issues
- Ensure backend Docker containers are running: `docker compose ps`
- Check backend logs: `docker compose logs -f backend`

### Database issues
- PostgreSQL uses version 10 (matches existing data)
- To reset database: `docker compose down -v` (WARNING: deletes all data)

## Development Workflow

1. Start backend: `docker compose up -d`
2. Start frontend: `cd OnlineJudgeFE && ./dev.sh`
3. Open http://localhost:8080 in browser
4. Make changes to Vue components in `OnlineJudgeFE/src/`
5. Frontend will hot-reload automatically

## Next Steps

To continue UI/UX modifications, edit files in:
- `OnlineJudgeFE/src/pages/oj/components/` - UI components
- `OnlineJudgeFE/src/styles/` - Global styles
- `OnlineJudgeFE/src/pages/oj/views/` - Page views
