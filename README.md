# AIMS Readiness

**ISO/IEC 42001 + EU AI Act Compliance Platform**

A production-quality platform for managing AI systems compliance with ISO/IEC 42001 and the EU AI Act. This platform helps organizations inventory AI systems, classify risk levels, perform gap analyses, track compliance evidence, and generate comprehensive compliance documentation.

## 🎯 Features

✅ **Guided Onboarding** - Step-by-step wizard for company setup, systems registration, risk assessment, and oversight planning  
✅ **Automatic Document Generation** - Generate 16+ compliance documents (ISO/IEC 42001 + EU AI Act) in Markdown and PDF  
✅ **AI Act Classification** - Automatic risk classification (high/limited/minimal/prohibited) + GPAI detection  
✅ **ISO 42001 Gap Analysis** - Identify missing controls  
✅ **FRIA Wizard** - 10-question Fundamental Rights Impact Assessment (Article 27)  
✅ **Evidence Management** - Upload and track compliance documentation with SHA256 checksums  
✅ **Post-Market Monitoring** - Incident tracking and KPIs (Article 72)  
✅ **Professional Exports** - Annex IV ZIP packages with integrity headers  
✅ **Real-time Dashboards** - Live compliance metrics, blocking issues, and upcoming deadlines  
✅ **Action Item Tracking** - CRUD for compliance actions with due dates and ownership  
✅ **Security Hardening** - XSS protection, streaming uploads, org isolation, rate limiting  

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** (tested on 3.11, 3.13)
- **Node.js 20+**
- **macOS/Linux** (Windows requires WSL)
- **System dependencies** (macOS): `brew install pango cairo gdk-pixbuf libffi` (for PDF generation)

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your settings:
# - SECRET_KEY: set to a secure random string (>=16 chars)
# - ORG_NAME: your organization name
# - ORG_API_KEY: your API key (will be auto-created on first startup)

# Run database migrations (auto-creates tables on startup)
# Start server
SECRET_KEY=your-secret-key uvicorn app.main:app --reload
```

Backend runs at **http://127.0.0.1:8000**  
API docs at **http://127.0.0.1:8000/docs**

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment (optional, defaults to localhost:8000)
# cp env.example .env.local
# Edit NEXT_PUBLIC_API_URL if needed

# Run development server
npm run dev
```

Frontend runs at **http://localhost:3000**

### First Login

1. Start both backend and frontend servers
2. Go to **http://localhost:3000/login**
3. Enter the API key from your backend `.env` file (e.g., `dev-aims-demo-key`)
4. Start the onboarding wizard to set up your organization

## 🧪 Testing & CI

### Run Tests

```bash
# Backend tests (critical flows)
cd backend
source .venv/bin/activate
SECRET_KEY=dev pytest tests/test_integration_critical_flows.py -v

# Frontend lint & build
cd frontend
npm run lint
npm run build
```

### Local CI Pipeline

Run the complete CI pipeline locally:

```bash
./ci.sh
```

This script runs:
- Python linting (ruff)
- Python tests (pytest)
- Frontend linting
- Frontend build verification

### GitHub Actions

CI runs automatically on push/PR to `main` branch via `.github/workflows/ci.yml`.

## 📊 Core Workflows

### 1. Onboarding Flow
1. **Company Setup** - Define company name, business sector, AI maturity
2. **Systems Registration** - Add AI systems with names, purposes, and risk profiles
3. **Risk Assessment** - Identify key risks and mitigation strategies
4. **Human Oversight** - Define oversight roles and responsibilities
5. **Monitoring Plan** - Set up monitoring cadence and metrics
6. **Summary & Generation** - Review and generate compliance documents

### 2. Document Management
- **List Documents** - View all generated compliance documents by system
- **Preview** - View documents in browser with XSS protection
- **Download** - Export as Markdown or PDF (if WeasyPrint available)
- **Regenerate** - Update documents with latest onboarding data

### 3. Evidence Tracking
- **Upload Evidence** - Attach files (PDFs, docs, images) to systems/controls
- **Streaming Upload** - Handles large files (up to 50MB) efficiently
- **MIME Validation** - Only allows whitelisted file types
- **Integrity Checks** - SHA256 checksums for all uploaded files

### 4. Reports & Analytics
- **Dashboard** - Real-time compliance metrics
- **Blocking Issues** - Critical items requiring immediate attention
- **Upcoming Deadlines** - Action items due in next 7-30 days
- **Annex IV Export** - EU AI Act technical documentation package

## 🔒 Security Features

- **API Key Authentication** - Multi-tenant isolation via X-API-Key header
- **Organization Isolation** - Each org can only access their own data
- **XSS Protection** - HTML sanitization using `bleach` library
- **Rate Limiting** - 60 requests/minute per API key or IP
- **Streaming Uploads** - Memory-safe file handling (no full-file loads)
- **File Size Limits** - 50MB maximum upload size
- **MIME Type Validation** - Whitelist-based file type checking
- **Security Headers** - CSP, X-Frame-Options, X-Content-Type-Options
- **Integrity Headers** - X-File-Hash, X-File-Size on exports

## 📁 Upload Limits

- **Maximum file size**: 50MB
- **Allowed file types**:
  - Documents: PDF, DOCX, DOC, XLSX, XLS, TXT, MD, CSV
  - Images: JPEG, PNG, GIF
- **Streaming**: Files are processed in 8KB chunks to prevent memory issues

## 🔧 Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret (required, >=16 chars) | `change_me` |
| `ENVIRONMENT` | Environment mode | `development` |
| `ORG_NAME` | Default organization name | `ACME Corp` |
| `ORG_API_KEY` | Default API key | `dev-aims-demo-key` |
| `DATABASE_URL` | Database connection string | SQLite (local) |
| `FRONTEND_ORIGIN` | CORS origin for frontend | `http://localhost:3000` |
| `RATE_LIMIT` | Requests per minute | `60` |

### Frontend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

## 🏗️ Project Structure

```
aims-readiness/
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── api/routes/          # API endpoints
│   │   │   ├── systems.py       # AI systems CRUD
│   │   │   ├── documents.py     # Document generation
│   │   │   ├── evidence.py      # Evidence upload
│   │   │   ├── reports.py       # Reports & exports
│   │   │   ├── actions.py       # Action items
│   │   │   ├── controls.py      # ISO controls
│   │   │   ├── fria.py          # FRIA assessments
│   │   │   ├── incidents.py     # Incident tracking
│   │   │   ├── templates.py     # Template management
│   │   │   └── compliance_suite.py  # Compliance suite
│   │   ├── core/
│   │   │   ├── config.py        # Settings
│   │   │   ├── security.py      # Auth & security
│   │   │   ├── middleware.py    # Rate limiting, headers
│   │   │   └── logging_config.py # Structured logging
│   │   ├── services/            # Business logic
│   │   │   ├── document_generator.py # Doc generation
│   │   │   ├── evidence.py      # File handling
│   │   │   ├── risk.py          # AI Act classification
│   │   │   ├── gap.py           # ISO gap analysis
│   │   │   └── ...
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   └── database.py          # DB connection
│   ├── tests/
│   │   ├── test_integration_critical_flows.py  # Core tests ✅
│   │   ├── test_security.py     # Security tests
│   │   └── ...                  # Legacy tests (to be refactored)
│   ├── scripts/
│   │   └── seed_demo.py         # Demo data seeder
│   └── requirements.txt
├── frontend/                     # Next.js frontend
│   ├── app/                     # Pages (App Router)
│   │   ├── page.tsx             # Dashboard
│   │   ├── onboarding/          # Onboarding wizard
│   │   ├── documents/           # Document management
│   │   ├── systems/             # Systems inventory
│   │   ├── reports/             # Reports & exports
│   │   └── ...
│   ├── components/
│   │   ├── ui/                  # shadcn/ui components
│   │   └── onboarding/          # Onboarding steps
│   ├── lib/
│   │   ├── api.ts               # API client
│   │   └── utils.ts             # Utilities
│   └── package.json
├── ci.sh                        # Local CI script
├── .github/workflows/ci.yml     # GitHub Actions CI
└── README.md                    # This file
```

## 🧪 Test Coverage

### Critical Integration Tests (14/14 passing ✅)
- Onboarding → Document generation flow
- Annex IV ZIP export with integrity headers
- Action items CRUD workflow
- Dashboard data accuracy
- PPTX endpoint handling (501 response)
- No localStorage dependency for document generation
- PDF fallback behavior (Markdown when WeasyPrint unavailable)
- Invalid document type validation
- Reports organization isolation
- Document generation security (path traversal prevention)
- Document preview XSS protection
- Evidence upload security (size, MIME, streaming)
- Annex IV download with system_id query param
- Reports ORM queries (no raw SQL)

### Security Tests
- XSS payload sanitization in document preview
- File size limit enforcement (50MB)
- MIME type validation
- Streaming upload memory efficiency
- Unauthorized access rejection
- Invalid API key rejection
- Organization data isolation

## 📝 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Authentication

All protected endpoints require the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/systems
```

### Example Requests

**Create AI System**:
```bash
curl -X POST http://localhost:8000/systems \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Service Bot",
    "purpose": "Automated customer support",
    "uses_biometrics": false,
    "is_general_purpose_ai": false
  }'
```

**Generate Documents**:
```bash
curl -X POST http://localhost:8000/documents/systems/1/generate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "ACME Corp",
    "systems": [...]
  }'
```

**Download Annex IV**:
```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8000/reports/export/annex-iv.zip?system_id=1 \
  --output annex-iv.zip
```

## 🛡️ Rate Limiting

- **Global limit**: 60 requests per minute per API key or IP
- **Expensive endpoints** (extra limiting):
  - Evidence uploads (`/evidence/*`)
  - Report exports (`/reports/*.pptx`, `/reports/*.zip`)
- **Response**: `429 Too Many Requests` with `Retry-After` header

## 🌐 Deployment

### Production Checklist

- [ ] Set `SECRET_KEY` to a secure random value (>= 32 chars)
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure PostgreSQL database (replace SQLite)
- [ ] Set `DATABASE_URL` to PostgreSQL connection string
- [ ] Configure S3/R2 for evidence storage (optional)
- [ ] Set `FRONTEND_ORIGIN` to your frontend domain
- [ ] Enable HTTPS/TLS
- [ ] Configure backup strategy
- [ ] Set up monitoring (logs, metrics)
- [ ] Review CORS settings (restrict `allow_origins`)

### Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

See [README_DEPLOY.md](README_DEPLOY.md) for detailed deployment instructions (Render + Vercel).

## 📊 Observability

### Logging

- **Development**: Human-readable logs to stdout
- **Production**: Structured JSON logs (set `ENVIRONMENT=production`)
- **Log levels**: INFO for app events, WARNING for issues, ERROR for failures

### Metrics

Rate limiting and request tracking are logged. For production metrics:
- **TODO**: Add Prometheus middleware for detailed metrics
- **TODO**: Integrate with monitoring service (DataDog, New Relic, etc.)

## 🐛 Known Limitations

### Current State
- ✅ **Core flows working**: Onboarding, documents, reports, evidence
- ✅ **Security**: XSS protection, upload limits, org isolation
- ✅ **CI/CD**: Local CI script + GitHub Actions
- ⚠️ **Legacy tests**: 34 tests need refactoring (use old API signatures)
- ⚠️ **WeasyPrint**: PDF generation requires system libraries (pango, cairo)

### Future Enhancements
- [ ] OAuth2/OIDC authentication (replace API keys)
- [ ] Real-time collaboration features
- [ ] Advanced analytics and dashboards
- [ ] Email notifications for deadlines
- [ ] Webhook integrations
- [ ] Multi-language support
- [ ] Audit trail export

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and data flow
- [Deployment Guide](README_DEPLOY.md) - Render + Vercel deployment
- [Data Validation Guide](docs/DATA_VALIDATION_GUIDE.md) - Data accuracy and testing
- [Backend README](backend/README.md) - API setup and usage
- [Frontend README](frontend/README.md) - UI development guide

## 🔧 Development

### Running Backend

```bash
cd backend
source .venv/bin/activate
SECRET_KEY=dev uvicorn app.main:app --reload --port 8000
```

### Running Frontend

```bash
cd frontend
npm run dev
```

### Running Tests

```bash
# Critical integration tests
cd backend
source .venv/bin/activate
SECRET_KEY=dev pytest tests/test_integration_critical_flows.py -v

# All tests (some legacy tests may fail)
SECRET_KEY=dev pytest tests/

# Frontend lint
cd frontend
npm run lint
```

### Code Quality

```bash
# Backend linting
cd backend
source .venv/bin/activate
ruff check . --fix
ruff format .

# Frontend linting
cd frontend
npm run lint
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linters (`./ci.sh`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## ⚖️ Compliance Notice

This platform prepares **Annex IV technical documentation** and **ISO/IEC 42001-aligned monitoring** artifacts but is **not** a Notified Body service. Compliance outcomes depend on your operational controls and external audits.

**The software is provided "as is" without warranty.** Users are responsible for ensuring their own compliance with applicable laws and regulations.

## 🆘 Troubleshooting

### Backend won't start
- **Error: `SECRET_KEY must be set`**  
  Solution: Set `SECRET_KEY` environment variable: `export SECRET_KEY=your-secret-key`

- **Error: `ModuleNotFoundError: No module named 'bleach'`**  
  Solution: Reinstall dependencies: `pip install -r requirements.txt`

- **Error: `OSError: cannot load library 'libpango-1.0-0'`**  
  Solution (macOS): `brew install pango cairo gdk-pixbuf libffi`

### Frontend shows blank page
- **Check backend**: Ensure backend is running on port 8000
- **Check API URL**: Verify `NEXT_PUBLIC_API_URL` in `.env.local` (or delete file to use default)
- **Clear cache**: Delete `frontend/.next` folder and restart: `rm -rf .next && npm run dev`
- **Check browser console**: Look for CORS or fetch errors

### Tests failing
- **Error: `ValueError: SECRET_KEY must be set`**  
  Solution: Run tests with: `SECRET_KEY=dev pytest tests/`

- **Error: `sqlite3.OperationalError: no such table: organizations`**  
  Solution: Delete test database: `rm backend/test_*.db` and rerun tests

### Document generation fails
- **PDF format unavailable**:  
  WeasyPrint requires system libraries. Install with: `brew install pango cairo` (macOS)  
  Fallback: Use Markdown format (`?format=markdown`)

## 📞 Support

For issues and questions:
- **GitHub Issues**: https://github.com/your-org/aims-readiness/issues
- **Documentation**: Check `docs/` folder
- **API Docs**: http://localhost:8000/docs

---

**Built with ❤️ for AI compliance professionals**

**Current Status**: Release Candidate - Core flows tested and functional
