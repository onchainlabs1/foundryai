# AIMS Readiness

**ISO/IEC 42001 + EU AI Act Compliance Platform**

A production-quality starter repository for managing AI systems compliance with ISO/IEC 42001 and the EU AI Act. This platform helps organizations inventory AI systems, classify risk levels, perform gap analyses, and track compliance evidence.

## Features

✅ **AI Systems Inventory** - CRUD operations + CSV import  
✅ **AI Act Classification** - Automatic risk classification (high/limited/minimal/prohibited) + GPAI detection  
✅ **ISO 42001 Gap Analysis** - Identify missing controls  
✅ **FRIA Wizard** - 10-question Fundamental Rights Impact Assessment (Article 27)  
✅ **Editable Controls (RACI)** - Manage controls with priority, status, owners, due dates  
✅ **Statement of Applicability (SoA)** - Generate ISO 42001 SoA as CSV  
✅ **Evidence Management** - Upload and track compliance documentation with SHA256 checksums  
✅ **Post-Market Monitoring (PMM)** - Incident tracking and KPIs (Article 72)  
✅ **Professional Exports** - Annex IV ZIP packages + Executive PPTX decks  
✅ **Transparent Scoring** - Compliance scores with clear formula and evidence coverage  
✅ **Demo Mode** - Pre-loaded sample data for instant exploration  

## Tech Stack

### Backend
- **FastAPI** (Python 3.11) - Modern async web framework
- **SQLAlchemy** - ORM with SQLite (dev) → PostgreSQL (prod)
- **Pydantic** - Data validation
- **pytest** - Testing framework
- **ruff/black/isort** - Code quality tools

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Beautiful UI components

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- pip and npm

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings (ORG_NAME, ORG_API_KEY)

# Run server
uvicorn app.main:app --reload
```

Backend runs at **http://127.0.0.1:8000**  
API docs at **http://127.0.0.1:8000/docs**

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit NEXT_PUBLIC_API_URL if needed

# Run development server
npm run dev
```

Frontend runs at **http://localhost:3000**

### Demo in 7 Minutes ⚡

The fastest way to explore AIMS Readiness:

```bash
# 1. Seed demo data (4 systems, controls, evidence, incidents)
cd backend
source .venv/bin/activate
python -m scripts.seed_demo

# 2. Start backend (port 8002)
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# 3. Start frontend (port 3002) - in new terminal
cd frontend
PORT=3002 NEXT_PUBLIC_API_URL=http://127.0.0.1:8002 npm run dev

# 4. Open http://localhost:3002/login
# 5. Click "🚀 Enter Demo Mode"
```

**Demo includes:**
- 4 AI systems (VisionID, CreditAssist, ChatAssist-G, OpsForecast)
- 10 controls across different risk levels
- 4 evidence records with proper linkage
- 2 FRIA assessments (1 approved, 1 submitted)
- 3 incidents (1 open high-severity, 2 resolved)

### First Login

1. Go to http://localhost:3000/login
2. Enter the API key from your backend `.env` file (default: `dev-aims-demo-key`)
3. Start managing AI systems!

## Project Structure

```
aims-readiness/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/routes/  # API endpoints
│   │   ├── core/        # Config & security
│   │   ├── services/    # Business logic
│   │   ├── mappers/     # ISO-AI Act mapping
│   │   ├── models.py    # Database models
│   │   └── schemas.py   # Pydantic schemas
│   ├── tests/           # pytest tests
│   └── requirements.txt
├── frontend/            # Next.js frontend
│   ├── app/            # Pages (App Router)
│   ├── components/ui/  # UI components
│   └── lib/api.ts      # API client
├── assets/
│   ├── templates/      # CSV templates
│   ├── mock/           # Sample reports
│   └── branding/       # Logo assets
└── docs/               # Documentation
```

## API Endpoints

### Public
- `GET /health` - Health check

### Protected (requires X-API-Key header)
- `GET /systems` - List AI systems
- `POST /systems` - Create AI system
- `POST /systems/import` - Import from CSV
- `POST /systems/{id}/assess` - Run AI Act assessment
- `POST /evidence/{system_id}` - Upload evidence
- `GET /reports/summary` - Get summary report

## Testing

### Backend
```bash
cd backend
pytest
ruff --select I,E,F .
```

### Frontend
```bash
cd frontend
npm run build
npm run lint
```

## Development Tools

- **Pre-commit hooks** - Auto-format code before commits
- **GitHub Actions** - Automated CI/CD
- **OpenAPI docs** - Interactive API documentation
- **Docker** - Containerization ready

## Security

⚠️ **Current authentication uses API keys in localStorage - for development only**

- Multi-tenant via X-API-Key header
- CORS enabled (configured for `*` in dev)
- Evidence files hashed with SHA256
- No secrets logged

**Production TODO**: Implement OAuth2/OIDC

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and data flow
- [Backend README](backend/README.md) - API setup and usage
- [Frontend README](frontend/README.md) - UI development guide

## License

MIT License - see LICENSE file

## Compliance Notice

This platform prepares **Annex IV technical documentation** and **ISO/IEC 42001-aligned monitoring** artifacts but is **not** a Notified Body service. Compliance outcomes depend on your operational controls and external audits.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linters
5. Submit a pull request

## Support

For issues and questions, please open a GitHub issue.

---

**Built with ❤️ for AI compliance professionals**

