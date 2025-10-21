# Audit-Grade Onboarding Implementation Progress

## ✅ Completed

### 1. localStorage Reset Enhancement
- Added auto-reload after reset to ensure clean state
- File: `frontend/app/onboarding/page.tsx`

### 2. Backend Models Extended
- **Organization**: Added contact fields (primary, DPO) and org_role
- **AISystem**: Added system_role, GPAI flags, Annex III categories, requires_fria
- **Incident**: Added notify_list field
- **New Models Created**:
  - `AIRisk`: Risk assessment with likelihood/impact
  - `Oversight`: Human oversight configuration (Art. 14/15)
  - `PMM`: Post-Market Monitoring (Art. 72)
- File: `backend/app/models.py`

### 3. Database Migration
- Created migration script: `backend/migrate_audit_grade.py`
- Successfully applied all schema changes
- ✅ All new tables and columns added

### 4. Pydantic Schemas
- Created `backend/app/schemas_audit.py` with:
  - OrgSetup, AISystemSetup
  - RiskCreate/Response, ControlBulkCreate
  - OversightCreate/Response, PMMCreate/Response
  - Bulk operation schemas

## 🚧 Next Steps (In Order)

### 5. Backend API Endpoints
Create new routes in backend:
```python
# backend/app/api/routes/onboarding_audit.py
POST /org/setup  # Update organization with audit fields
POST /systems/{id}/setup  # Extended system setup
POST /systems/{id}/risks/bulk  # Bulk risk creation
POST /controls/bulk  # Bulk control creation (extend existing)
POST /systems/{id}/oversight  # Human oversight setup
POST /systems/{id}/pmm  # PMM configuration
GET /systems/{id}/soa.csv  # Export SoA as CSV
```

### 6. Frontend - Step 1 Upgrade
Enhance Company Setup with:
- Primary contact (name, email)
- DPO contact (name, email)
- Org role selector (provider/deployer/both)
- Stakeholders list helper

### 7. Frontend - Step 2 Upgrade
Add to AI System Definition:
- System role, lifecycle stage, deployment context
- Third-party providers/datasets (array input)
- Impacted groups (chips)
- All boolean flags (GPAI, biometrics, sensitive data, etc.)
- Annex III categories (multi-select)
- Auto-compute requires_fria flag

### 8. Frontend - Step 3 Upgrade
Risk & Controls enhancements:
- Minimum 3 risks table (inline-editable)
- Controls table with status/owner/due date
- Model validation method presets
- Drift monitoring plan
- "Export SoA (CSV)" button after save

### 9. Frontend - Step 4 Create
Human Oversight form:
- Oversight mode selector
- Intervention rules (IF/THEN builder)
- Manual override toggle
- Appeals configuration
- Ethics committee setup
- Training & communication plans

### 10. Frontend - Step 5 Create
PMM (Monitoring & Improvement):
- Logging scope checklist
- Retention period slider
- Fairness metrics chips
- Drift threshold slider
- Audit/review frequency selectors
- EU DB conditional fields (if provider + high-risk)

### 11. FRIA Gate Logic
- Server-side validation in document generation
- Check requires_fria flag
- Return 409 if FRIA required but missing
- Frontend gate on "Generate Drafts" button

### 12. SoA CSV Export
- Generate CSV from controls table
- Columns: Clause, Control, Applicable, Justification, Owner, Status, Due Date, Evidence Link

### 13. Testing
- Test complete 5-step flow
- Verify all data persists
- Test FRIA gate
- Verify SoA export
- Test document generation with all new fields

## 📝 Files Modified

### Backend
- ✅ `backend/app/models.py` - Extended with audit-grade models
- ✅ `backend/app/schemas_audit.py` - NEW: Pydantic schemas
- ✅ `backend/migrate_audit_grade.py` - NEW: Migration script
- 🚧 `backend/app/api/routes/onboarding_audit.py` - NEW: API endpoints needed
- 🚧 `backend/app/api/routes/controls.py` - Extend with bulk endpoint
- 🚧 `backend/app/api/routes/documents.py` - Add FRIA gate logic
- 🚧 `backend/app/services/soa_export.py` - NEW: CSV generation

### Frontend
- ✅ `frontend/app/onboarding/page.tsx` - Reset enhancement
- 🚧 `frontend/components/onboarding/company-setup.tsx` - Upgrade needed
- 🚧 `frontend/components/onboarding/system-definition.tsx` - Upgrade needed
- 🚧 `frontend/components/onboarding/risk-controls.tsx` - Upgrade needed
- 🚧 `frontend/components/onboarding/human-oversight.tsx` - NEW: Create
- 🚧 `frontend/components/onboarding/monitoring-improvement.tsx` - NEW: Create
- 🚧 `frontend/lib/api.ts` - Add new API methods

## 🎯 Current Status
- **Progress**: 4/13 tasks completed (31%)
- **Models**: ✅ Complete
- **Schemas**: ✅ Complete
- **Migration**: ✅ Complete
- **API Endpoints**: 🚧 Ready to implement
- **Frontend**: 🚧 Ready to upgrade

## 🚀 How to Continue
1. Run backend to ensure it starts: `cd backend && source .venv/bin/activate && SECRET_KEY=dev-secret-key-for-development-only python -m uvicorn app.main:app --port 8001`
2. Implement API endpoints (Task 5)
3. Upgrade frontend components (Tasks 6-10)
4. Add FRIA gate and SoA export (Tasks 11-12)
5. Test complete flow (Task 13)

## 📌 Key Design Decisions
- **Additive only**: No breaking changes to existing API
- **Computed flags**: requires_fria calculated server-side
- **JSON in TEXT**: Annex III categories, fairness_metrics stored as JSON strings
- **Nullable by default**: All new fields optional for backward compatibility
- **Bulk operations**: POST /risks/bulk, POST /controls/bulk for efficiency

