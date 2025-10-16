# AIMS Readiness - Architecture

## System Overview

AIMS Readiness is a full-stack web application designed to help organizations manage compliance with ISO/IEC 42001 (AI Management System) and the EU AI Act. The platform follows a modern client-server architecture with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Next.js 14 (App Router)                                 │  │
│  │  - Dashboard, Inventory, System Details, Reports         │  │
│  │  - Tailwind CSS + shadcn/ui                              │  │
│  │  - localStorage API key auth                             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/JSON + X-API-Key
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API Layer                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI                                                  │  │
│  │  - OpenAPI/Swagger docs                                  │  │
│  │  - CORS middleware                                       │  │
│  │  - API key authentication middleware                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Services                                                 │  │
│  │  - risk.py: AI Act classification                        │  │
│  │  - gap.py: ISO 42001 gap analysis                        │  │
│  │  - evidence.py: File handling & checksums                │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Mappers                                                  │  │
│  │  - iso42001_ai_act.py: Compliance mapping                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Data Access Layer                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SQLAlchemy ORM                                           │  │
│  │  - Organization, AISystem, Evidence models               │  │
│  │  - Relationships and foreign keys                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Persistence Layer                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SQLite (Development)                                     │  │
│  │  PostgreSQL (Production-ready)                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  File System                                              │  │
│  │  - Evidence files stored in ./evidence/org_X/system_Y/   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Model

### Entity-Relationship Diagram

```
Organization (1) ──────< (N) AISystem
     │                         │
     │                         │
     └──────< (N) Evidence <───┘
```

### Database Schema

#### Organization
- `id` (PK) - Integer
- `name` - String(255)
- `api_key` - String(255), unique, indexed
- `created_at` - DateTime

#### AISystem
- `id` (PK) - Integer
- `org_id` (FK) - References Organization
- `name` - String(255)
- `purpose` - Text
- `domain` - String(255)
- `owner_email` - String(255)
- `uses_biometrics` - Boolean
- `is_general_purpose_ai` - Boolean
- `impacts_fundamental_rights` - Boolean
- `personal_data_processed` - Boolean
- `training_data_sensitivity` - String(50)
- `output_type` - String(100)
- `deployment_context` - String(100)
- `criticality` - String(50)
- `notes` - Text
- `ai_act_class` - String(50) [high|limited|minimal]

#### Evidence
- `id` (PK) - Integer
- `org_id` (FK) - References Organization
- `system_id` (FK) - References AISystem (nullable)
- `label` - String(255)
- `iso42001_clause` - String(100)
- `control_name` - String(255)
- `file_path` - String(500)
- `version` - String(50)
- `checksum` - String(64) - SHA256 hash
- `uploaded_by` - String(255)
- `upload_date` - DateTime
- `status` - String(50) [uploaded|approved|rejected]
- `reviewer_email` - String(255)
- `link_or_location` - String(500)

## Multi-Tenancy

**Strategy**: API Key-based tenant isolation

1. Each organization has a unique API key stored in the `organizations` table
2. All protected endpoints require `X-API-Key` header
3. The `verify_api_key` dependency validates the key and returns the organization
4. All queries are automatically scoped to `org_id`

**Example Flow**:
```
Request → Middleware → verify_api_key(X-API-Key) → Get org.id → Scope query
```

**Security Considerations**:
- API keys must be kept secret
- Keys should be rotated regularly (future feature)
- Production should use OAuth2/OIDC instead of API keys

## AI Act Classification Logic

The system implements rule-based classification according to EU AI Act risk levels:

```python
def classify_ai_act(system_data):
    # HIGH RISK
    if uses_biometrics AND deployment_context == "public":
        return "high"
    
    if impacts_fundamental_rights:
        return "high"
    
    # LIMITED RISK
    if is_general_purpose_ai:
        return "limited"
    
    # MINIMAL RISK (default)
    return "minimal"
```

**Risk Levels**:
- **High**: Biometric systems in public spaces, fundamental rights impact
- **Limited**: General-purpose AI systems
- **Minimal**: Low-risk AI applications

## ISO 42001 Gap Analysis

The platform maps ISO 42001 clauses to AI Act requirements:

```python
ISO_TO_AI_ACT = {
    "ISO42001:5.1 Governance": ["AIAct:Accountability", "AIAct:Transparency"],
    "ISO42001:6.1 Risk Management": ["AIAct:RiskMgmt", "AIAct:PostMarketMonitoring"],
    "ISO42001:7.2 Competence": ["AIAct:AI_Literacy"],
    "ISO42001:8.3 Design & Dev": ["AIAct:DataGovernance", "AIAct:TechnicalDocumentation"],
    "ISO42001:9.1 Monitoring": ["AIAct:Logging", "AIAct:RecordKeeping"],
}
```

**Gap Detection**:
- Compare implemented controls vs. required controls
- Return missing ISO clauses
- Generate RACI matrix with placeholders

## Security Model

### Authentication
- **Current**: API key in `X-API-Key` header
- **Storage**: Backend validates against `organizations.api_key`
- **Client**: localStorage (⚠️ dev only)

### Authorization
- Organization-scoped data access
- All queries filtered by `org_id`
- No cross-tenant data leakage

### File Security
- Evidence files stored with SHA256 checksum
- File integrity verification on upload
- Organized by org and system: `./evidence/org_{id}/system_{id}/`

### CORS
- Currently configured for `*` (development)
- Production should whitelist specific origins

## API Design

### RESTful Principles
- Resources: `/systems`, `/evidence`, `/reports`
- HTTP methods: GET (read), POST (create)
- JSON payloads
- Standard status codes

### Request Flow
```
Client Request
    ↓
CORS Middleware
    ↓
Route Handler
    ↓
verify_api_key() - Extract org from header
    ↓
Business Logic (Services)
    ↓
Database Query (scoped to org_id)
    ↓
Pydantic Response Model
    ↓
JSON Response
```

## Frontend Architecture

### Next.js App Router
- **Server Components**: Initial page loads
- **Client Components**: Interactive features (`'use client'`)
- **File-based routing**: `/app/inventory/page.tsx` → `/inventory`

### State Management
- React hooks (`useState`, `useEffect`)
- API calls through `/lib/api.ts`
- localStorage for API key

### Component Structure
```
app/
├── layout.tsx         # Root layout with nav
├── page.tsx          # Dashboard
├── login/page.tsx    # Auth
├── inventory/        # AI systems list
├── systems/[id]/     # Dynamic system detail
└── reports/          # Exports
```

## Deployment Considerations

### Development
- SQLite database
- Local file storage
- CORS `*`
- API keys in localStorage

### Production Recommendations
- PostgreSQL database
- S3/object storage for evidence files
- OAuth2/OIDC authentication
- Specific CORS origins
- HTTPS only
- Rate limiting
- Audit logging
- Database backups

### Scaling Strategy
1. **Vertical**: Increase server resources
2. **Horizontal**: Load balancer + multiple backend instances
3. **Database**: Connection pooling, read replicas
4. **Caching**: Redis for session/API responses
5. **CDN**: Static assets and frontend

## Error Handling

### Backend
- Pydantic validation errors → 422
- Not found → 404
- Unauthorized → 401
- Server errors → 500 (with structured JSON)

### Frontend
- Try-catch around API calls
- User-friendly error messages
- Console logging for debugging

## Testing Strategy

### Backend
- `pytest` for unit and integration tests
- Test health endpoint (smoke test)
- Future: Test each endpoint, service, classification logic

### Frontend
- TypeScript for compile-time checks
- Build-time validation
- Future: Jest + React Testing Library

### CI/CD
- GitHub Actions on every push
- Backend: lint (ruff) + test (pytest)
- Frontend: build + lint

## Observability

### Current
- Console logging
- OpenAPI docs for API exploration
- Health endpoint for uptime checks

### Future Enhancements
- Structured JSON logging
- Request IDs for tracing
- Prometheus metrics
- Error tracking (Sentry)
- Audit trail for compliance actions

## Compliance Workflow

1. **Inventory** → Create/import AI systems
2. **Classify** → Auto-classify AI Act risk level
3. **Assess** → Run gap analysis against ISO 42001
4. **Plan** → Generate RACI control plan
5. **Execute** → Upload evidence files
6. **Report** → Export compliance documentation
7. **Monitor** → Track compliance over time

## Extension Points

### Custom Classification Rules
Modify `app/services/risk.py` to add:
- Industry-specific rules
- Regional regulations
- Custom risk factors

### Additional Standards
Add new mappers in `app/mappers/`:
- NIST AI RMF
- IEEE 7000 series
- Industry standards

### Report Formats
Extend `app/api/routes/reports.py`:
- PDF generation
- PowerPoint exports
- Custom templates

## Technology Choices Rationale

**FastAPI**: Modern, fast, auto-generated docs, async support  
**SQLAlchemy**: ORM flexibility, easy DB migration  
**Next.js 14**: App Router for modern React patterns  
**Tailwind CSS**: Utility-first, fast UI development  
**shadcn/ui**: Copy-paste components, full customization  
**TypeScript**: Type safety for frontend robustness  

## Limitations & Future Work

### Current Limitations
- No user management (single API key per org)
- No audit trail
- Basic file storage (local filesystem)
- No email notifications
- No real-time collaboration

### Roadmap
- [ ] OAuth2/OIDC authentication
- [ ] Role-based access control (RBAC)
- [ ] Workflow automation
- [ ] Email notifications
- [ ] Advanced analytics dashboard
- [ ] API versioning
- [ ] Multi-language support
- [ ] Mobile app

