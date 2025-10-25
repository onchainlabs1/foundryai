# AIMS Readiness - Backend

FastAPI backend for ISO/IEC 42001 + EU AI Act compliance platform.

## Features

- Multi-tenant API with API key authentication
- AI systems inventory (CRUD + CSV import)
- AI Act risk classification (automatic)
- ISO 42001 gap analysis
- Evidence upload with SHA256 checksums
- FRIA (Fundamental Rights Impact Assessment) wizard
- Controls management with RACI
- Statement of Applicability (SoA) generation
- Post-Market Monitoring (incident tracking)
- Professional exports (Annex IV ZIP, Executive PPTX, PDF)
- Transparent scoring algorithm
- Reports summary API

## Setup

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

### PDF Export (Optional)

PDF export requires WeasyPrint, which is an optional dependency:

```bash
# Install WeasyPrint for PDF export support
pip install weasyprint

# Or install with system dependencies (recommended for production)
# Ubuntu/Debian:
sudo apt-get install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0
pip install weasyprint

# macOS:
brew install pango
pip install weasyprint
```

**Note**: If WeasyPrint is not installed, PDF export endpoints will return HTTP 501 with a clear error message. All other export formats (ZIP, DOCX, MD) will continue to work normally.

### Development

```bash
# Run server
uvicorn app.main:app --reload

# API docs available at:
# http://127.0.0.1:8000/docs
```

### Testing

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with environment variables for consistent results
SECRET_KEY='development-secret-key' ORG_NAME='Test Org' ORG_API_KEY='dev-aims-demo-key' pytest

# Run linter
ruff --select I,E,F .

# Format code
black .
isort .
```

**Note**: The test suite requires `pytest-asyncio>=0.23.0` for async test support. It's included in `requirements.txt`.

### Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## API Endpoints

### Public
- `GET /health` - Health check

### Protected (requires X-API-Key header)

#### Systems
- `GET /systems` - List AI systems
- `POST /systems` - Create AI system
- `POST /systems/import` - Import from CSV
- `POST /systems/{id}/assess` - Assess AI Act classification & gaps

#### Evidence
- `POST /evidence/{system_id}` - Upload evidence

#### FRIA (Fundamental Rights Impact Assessment)
- `POST /systems/{id}/fria` - Submit FRIA assessment
- `GET /systems/{id}/fria/latest` - Get latest FRIA
- `GET /fria/{id}.md` - Download FRIA as Markdown
- `GET /fria/{id}.html` - Download FRIA as HTML

#### Controls & SoA
- `POST /controls/bulk` - Bulk upsert controls
- `GET /systems/{id}/controls` - List controls for system
- `GET /systems/{id}/soa.csv` - Export Statement of Applicability

#### Incidents (PMM)
- `POST /incidents` - Create incident
- `GET /incidents?system_id={id}` - List incidents
- `PATCH /incidents/{id}` - Update incident

#### Reports & Exports
- `GET /reports/summary` - Get summary report
- `GET /reports/score` - Get compliance scores
- `GET /reports/annex-iv/{system_id}` - Export Annex IV package (ZIP)
- `GET /reports/deck.pptx` - Export Executive deck
- `GET /reports/export/pptx` - Alias for deck.pptx
- `GET /reports/export/{doc_type}.{format}` - Export documents (MD, DOCX, PDF)

**Note**: Export endpoints return `X-Bundle-Hash` header with SHA-256 hash of document content for integrity verification.

### Deprecated Endpoints
- `GET /reports/export/annex-iv.zip` - Use `/reports/annex-iv/{system_id}` instead

## Environment Variables

- `DATABASE_URL` - Database connection (default: sqlite:///./aims.db)
- `SECRET_KEY` - Application secret key
- `ORG_NAME` - Default organization name (for seeding)
- `ORG_API_KEY` - Default API key (for development)

## Database

SQLite for development, PostgreSQL-ready for production.

To switch to PostgreSQL:
```bash
DATABASE_URL=postgresql://user:pass@localhost/aims
```

## API Examples

### Create FRIA Assessment
```bash
curl -X POST "http://localhost:8000/systems/1/fria" \
  -H "X-API-Key: dev-aims-demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "system_id": 1,
    "applicable": true,
    "answers": {
      "biometric_data": "Yes",
      "fundamental_rights": "Yes",
      "critical_infrastructure": "No"
    }
  }'
```

### Bulk Upsert Controls
```bash
curl -X POST "http://localhost:8000/controls/bulk" \
  -H "X-API-Key: dev-aims-demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "controls": [
      {
        "system_id": 1,
        "iso_clause": "ISO42001:6.1",
        "name": "Risk Management Process",
        "priority": "high",
        "status": "implemented",
        "owner_email": "compliance@company.com",
        "due_date": "2024-12-31",
        "rationale": "Critical for high-risk systems"
      }
    ]
  }'
```

### Create Incident
```bash
curl -X POST "http://localhost:8000/incidents" \
  -H "X-API-Key: dev-aims-demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "system_id": 1,
    "severity": "medium",
    "description": "Model performance degradation detected",
    "corrective_action": "Retrained model with updated dataset"
  }'
```

### Get Compliance Score
```bash
curl -X GET "http://localhost:8000/reports/score" \
  -H "X-API-Key: dev-aims-demo-key"
```

### Export Annex IV ZIP
```bash
curl -X GET "http://localhost:8000/reports/annex-iv/1" \
  -H "X-API-Key: dev-aims-demo-key" \
  -o annex-iv-export.zip
```

## Scoring Algorithm

The compliance score is calculated using a transparent formula:

```
System Score = 0.6 × (controls_implemented_pct) + 0.4 × (evidence_coverage_pct)

Weighted by AI Act class:
- High: 1.2x
- Limited: 1.0x  
- Minimal: 0.8x

Org Score = weighted average of all system scores
Final score clamped to [0, 1]
```

## Docker

```bash
# Build
docker build -t aims-backend .

# Run
docker run -p 8000:8000 -e ORG_API_KEY=your-key aims-backend
```

