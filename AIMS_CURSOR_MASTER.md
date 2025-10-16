# AIMS Readiness — Cursor Agent **Master Document**
*Single file to anchor your Cursor Agent. Keep this in the repo root and pin it in Cursor’s Project Context.*
**Updated:** 2025-10-13

> **Nota (PT-BR):** Documento único com **Master Prompt**, **Project Rules** e **Fases** para rodar o projeto com o Cursor Agent.

---

## 0) How to use (quick)
1. Save this file at repo root as **AIMS_CURSOR_MASTER.md** and pin it in Cursor (Project → Context files).
2. (Optional) Copy the **Project Rules** block into Cursor’s Project Rules.
3. Start the agent: **"Use AIMS_CURSOR_MASTER.md and follow Phase 1. Return only TREE + essential DIFFS + NEXT."**
4. After each phase passes locally (tests/docs ok), say: **"Proceed to Phase N+1."**

---

## 1) MASTER PROMPT (paste to the Agent)
You are a Staff-level engineer building a lean SaaS called **AIMS Readiness** (ISO/IEC 42001 + EU AI Act).
Deliverables: production-quality starter repo with API + web app + docs, minimal but clean.

### Non-negotiables (follow strictly)
- Language: **English** in code, commit messages, and docs.
- Multi-tenant via **X-API-Key** header; no OAuth yet.
- Stack: **FastAPI (Python 3.11)**, **SQLAlchemy + SQLite (dev)** with easy swap to Postgres; **Next.js 14 + App Router + Tailwind + shadcn/ui**.
- Features MVP:
  1) AI systems **inventory** (CRUD/import CSV)
  2) **AI Act classification** (rules)
  3) **ISO 42001 gap** generator (seed mapping)
  4) **Control plan (RACI)** data model (stub service)
  5) **Evidence upload** (hash + local storage)
  6) **Reports summary** endpoint (+ placeholder for PPTX export)
- Security: CORS *, API key required for all non-/health routes.
- Observability: console logs; structured JSON error handler.
- Docs: **README** (root & backend & frontend), **API docs** (OpenAPI), **/docs/ARCHITECTURE.md**.
- DevX: `ruff+black+isort`, `pre-commit`, `pytest` smoke tests, GitHub Actions (lint+test).
- Tokens: Output only **files created/modified** as a compact tree + **short diffs**.

### Repo layout
```
aims-readiness/
  backend/
    app/{main.py, database.py, models.py, schemas.py}
    app/core/{config.py, security.py}
    app/api/routes/{systems.py, evidence.py, reports.py}
    app/services/{risk.py, gap.py, evidence.py}
    app/mappers/iso42001_ai_act.py
    requirements.txt  .env.example  Dockerfile  README.md
    tests/test_health.py
    pyproject.toml  pre-commit-config.yaml
  frontend/
    app/(Next.js app router)
    components/, lib/api.ts, styles/globals.css, README.md
    package.json  tsconfig.json  postcss.config.js  tailwind.config.ts
  assets/
    templates/{aims_inventory_template.csv, aims_control_plan_raci_template.csv, aims_evidence_manifest_template.csv}
    mock/aims_readiness_mock.html
    branding/{logo.svg, lockup-horizontal.svg}
  docs/ARCHITECTURE.md
  .github/workflows/ci.yml
  README.md  LICENSE
```

### Data model (MVP)
- **Organization**(id, name, api_key, created_at)
- **AISystem**(id, org_id, name, purpose, domain, owner_email, uses_biometrics, is_general_purpose_ai, impacts_fundamental_rights, personal_data_processed, training_data_sensitivity, output_type, deployment_context, criticality, notes, ai_act_class)
- **Evidence**(id, org_id, system_id, label, iso42001_clause, control_name, file_path, version, checksum, uploaded_by, upload_date, status, reviewer_email, link_or_location)

### Endpoints (must exist)
- `GET /health`
- `GET /systems`, `POST /systems`, `POST /systems/import (CSV)`
- `POST /systems/{id}/assess` → returns `{ ai_act_class, gap[], control_plan[] }`
- `POST /evidence/{system_id}` → saves file, returns checksum/path
- `GET /reports/summary` → `{ systems, high_risk }`

### AI Act rules (initial)
```py
def classify_ai_act(sys):
    if sys.get("uses_biometrics") and sys.get("deployment_context") == "public": return "high"
    if sys.get("impacts_fundamental_rights"): return "high"
    if sys.get("is_general_purpose_ai"): return "limited"
    return "minimal"
```

### ISO 42001 seed mapping
```py
ISO_TO_AI_ACT = {
 "ISO42001:5.1 Governance": ["AIAct:Accountability","AIAct:Transparency"],
 "ISO42001:6.1 Risk Management": ["AIAct:RiskMgmt","AIAct:PostMarketMonitoring"],
 "ISO42001:7.2 Competence": ["AIAct:AI_Literacy"],
 "ISO42001:8.3 Design & Dev": ["AIAct:DataGovernance","AIAct:TechnicalDocumentation"],
 "ISO42001:9.1 Monitoring": ["AIAct:Logging","AIAct:RecordKeeping"],
}
```
`generate_gap(class, current_controls=[])` ⇒ list missing clauses (simple set diff).

### Frontend (Next.js)
Pages:
- `/login` (stores API key in localStorage; warns this is dev-only)
- `/` Overview: KPIs + Readiness Trend (dummy) + Upcoming Actions
- `/inventory` table with filters + **Import CSV** (call `/systems/import`)
- `/systems/[id]` tabs: Overview, AI Act Class (accept/override), Risks, Controls, Evidence (drag&drop → `/evidence/{id}`), Reports
- `/reports` buttons to export CSVs (call APIs) + PPTX placeholder

Use Tailwind + shadcn/ui. Minimal API client in `lib/api.ts` reading `NEXT_PUBLIC_API_URL` and `X-API-Key` from storage.

### Dev env
- Backend `.env.example`:
```
DATABASE_URL=sqlite:///./aims.db
SECRET_KEY=change_me
ORG_NAME=On-Chain Labs Governance
ORG_API_KEY=dev-aims-demo-key
```
- Scripts:
  - backend: `uvicorn app.main:app --reload`
  - frontend: `next dev`

### Tests
- `tests/test_health.py` → status 200 json ok
- (Optional) Postman collection stub in `/assets`

### CI
- GitHub Actions: Python set up, `pip install -r requirements.txt`, run `ruff --select I,E,F . && pytest -q`
- Node job: `pnpm i && pnpm build` (or npm/yarn).

### Token-economy output rules
1) Do work **phase by phase**. After each phase, print: TREE + DIFFS + NEXT.
2) Keep responses compact.

### PHASES
**Phase 1 — Backend skeleton**
- Backend structure, models, services, routes, requirements, pyproject (ruff/black), pre-commit, tests, README.
- API-Key guard for all except `/health`.
- Seed org if `ORG_NAME/ORG_API_KEY` set.
- DoD: `uvicorn` runs, `/docs` shows routes, tests pass.

**Phase 2 — Frontend scaffold**
- Next.js + Tailwind + shadcn; pages; `lib/api.ts`; `NEXT_PUBLIC_API_URL`.

**Phase 3 — Assets & templates**
- CSV templates (3) + mock HTML in `/assets`; link in `/reports`.

**Phase 4 — Docs & CI**
- Root README, backend/README, frontend/README, `docs/ARCHITECTURE.md`, GitHub CI.

**Phase 5 — Nice-to-have**
- `docker-compose.yml`, Postman, JSON error handler, PPTX stub.

---

## 2) Project Rules (use as `/.cursorrules`)
```
# AIMS Readiness – Cursor Project Rules (short)
- Language: English in code/docs; Portuguese only in chats if asked.
- Scope is fixed: FastAPI + SQLAlchemy + SQLite(dev)/Postgres(prod), Next.js 14 + Tailwind + shadcn/ui.
- Multi-tenant via X-API-Key; all routes require it except /health.
- Must implement: inventory (CRUD/CSV), AI Act classification (rules), ISO 42001 GAP (seed map), control plan (RACI stub), evidence upload (hash), reports summary.
- Do NOT add extra libs/frameworks unless explicitly requested in this document.
- Token economy: output only changed files (tree + short diffs). No lockfiles, no large pastes.
- Follow PHASES. Finish current phase before starting the next.
- Security: CORS *, structured JSON errors; never log secrets or API keys.
- Tests (pytest) and lint (ruff) must pass locally.
```

---

## 3) Phase prompts (short)
- Phase 1: `Use AIMS_CURSOR_MASTER.md. Proceed with Phase 1 (backend skeleton). Return only TREE + essential DIFFS + NEXT.`
- Phase 2: `Proceed with Phase 2 (frontend scaffold) per AIMS_CURSOR_MASTER.md. Same output rules.`
- Phase 3: `Proceed with Phase 3 (assets & templates).`
- Phase 4: `Proceed with Phase 4 (docs & CI).`
- Phase 5: `Proceed with Phase 5 (nice-to-have).`

---

## 4) Local quickstart (dev)
```bash
# Backend
cd aims-readiness/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit ORG_API_KEY if needed
uvicorn app.main:app --reload  # http://127.0.0.1:8000/docs

# Frontend (after Phase 2)
cd ../frontend
npm i && npm run dev  # NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

---

## 5) Legal & scope note
This project prepares **Annex IV technical documentation** and **ISO/IEC 42001–aligned monitoring** artifacts but is **not** a Notified Body service. Compliance outcomes depend on your operational controls and external audits.
