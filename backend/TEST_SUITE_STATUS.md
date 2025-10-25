# Test Suite Status

## Summary

**Date:** 2024-10-24
**Total Tests:** 153
**Passed:** 118
**Failed:** 31
**Skipped:** 4

## Progress

- **Previous Status:** 68 failures
- **Current Status:** 31 failures
- **Improvement:** 37 tests fixed ✅

## Key Achievements

1. **Fixed `test_utc_timezone.py`:**
   - Resolved persistent indentation errors using Python script to fix whitespace
   - Updated tests to use correct field name (`upload_date` instead of `uploaded_at`)
   - Fixed regex pattern for datetime validation
   - All 6 tests now passing ✅

2. **Unified Test Fixtures:**
   - Created `test_client_with_seed` fixture in `backend/tests/conftest.py`
   - Seeds "Credit Scoring AI" scenario with 7 evidences, FRIA, controls, and incident
   - Properly manages `get_db` override with `yield` and `finally` cleanup
   - Uses `StaticPool` for in-memory SQLite isolation

3. **Updated Tests to Use Shared Fixture:**
   - ✅ `test_evidence_citations.py` (2 tests passing)
   - ✅ `test_manifest_schema.py` (4 tests passing)
   - ✅ `test_placeholders.py` (4 tests passing)
   - ✅ `test_integration_critical_flows.py` (3 tests passing)
   - ✅ `test_utc_timezone.py` (6 tests passing)
   - ✅ `test_staging.py` (8 tests passing)

## Remaining Failures (31)

### 1. Missing `os` Import (9 failures)
**Files:** `test_citations.py` (4), `test_fria_gate.py` (3)

```python
# Need to add at top of each file:
import os
```

**Affected Tests:**
- `test_evidence_citations_present`
- `test_evidence_citations_format_validation`
- `test_no_evidence_markers_when_no_evidence`
- `test_evidence_manifest_consistency`
- `test_fria_submitted_allows_export`
- `test_fria_status_affects_export`

### 2. Legacy Tests Using Global `client`/`HEADERS` (18 failures)
**Files:** `test_compliance_suite_basic.py`, `test_compliance_suite_e2e.py`, `test_controls.py`, `test_fria.py`, `test_incidents.py`

These tests use global `TestClient` and expect `dev-aims-demo-key` to work, but don't have proper database seeding.

**Status Codes:**
- Expected: `200` / `400` / `409`
- Getting: `403` (Forbidden - API key not found in database)

**Solution:** Update these tests to use `test_client_with_seed` or `with_isolated_client` fixtures.

### 3. Test Logic Issues (4 failures)

**`test_fria_gate.py`:**
- `test_fria_required_blocks_export`: FRIA gate not enforced (returns 200 instead of 409/400/422)
- `test_fria_gate_with_complete_annex_iv`: Same issue

**`test_citations.py`:**
- `test_evidence_citations_present`: No evidence citations found in generated documents (may need to verify citation generation logic)

**`test_fria_gate.py`:**
- `test_fria_submitted_allows_export`: Manifest schema changed (expects `filename` key in artifacts)
- `test_fria_status_affects_export`: FRIA content doesn't include "not applicable" text

## Next Steps

1. **Quick fixes (Priority 1 - 5 min):**
   - Add `import os` to `test_citations.py` and `test_fria_gate.py`
   
2. **Update legacy tests (Priority 2 - 30-60 min):**
   - Convert `test_compliance_suite_basic.py` to use shared fixtures
   - Convert `test_compliance_suite_e2e.py` to use shared fixtures
   - Convert `test_controls.py` to use shared fixtures
   - Convert `test_fria.py` to use shared fixtures
   - Convert `test_incidents.py` to use shared fixtures

3. **Fix test logic issues (Priority 3 - 30-60 min):**
   - Review FRIA gate enforcement in `/reports/annex-iv` endpoints
   - Review evidence citation generation
   - Update manifest schema expectations
   - Review FRIA template for "not applicable" status

## Test Files Using Shared Fixture ✅

- `backend/tests/conftest.py` - Defines `test_client_with_seed`
- `backend/tests/test_evidence_citations.py`
- `backend/tests/test_manifest_schema.py`
- `backend/tests/test_placeholders.py`
- `backend/tests/test_integration_critical_flows.py`
- `backend/tests/test_utc_timezone.py`
- `backend/tests/test_staging.py`
- `backend/tests/test_reports_extended.py` (uses `with_isolated_client`)
- `backend/tests/test_ai_act_class_role.py` (uses `with_isolated_client`)
- `backend/tests/test_blocking_issues.py` (uses `with_isolated_client`)
- `backend/tests/test_zip_completeness.py` (uses `with_isolated_client`)
- `backend/tests/test_soa_contract.py` (uses `with_isolated_client`)
- `backend/tests/test_fria_gate.py` (uses `with_isolated_client`)
- `backend/tests/test_citations.py` (uses `with_isolated_client`)

## Environment

- **Python:** 3.13.2
- **pytest:** 8.4.2
- **SQLAlchemy:** Uses `StaticPool` for test isolation
- **Test database:** In-memory SQLite
- **API Key:** `dev-aims-demo-key` (seeded by `test_client_with_seed`)

## Command to Run Full Suite

```bash
cd /Users/fabio/Desktop/foundry/backend
source .venv/bin/activate
SECRET_KEY='development-secret-key' ORG_NAME='Test Org' ORG_API_KEY='dev-aims-demo-key' pytest -q
```

## Seed Data (Credit Scoring AI)

The `test_client_with_seed` fixture seeds:
- **Organization:** Test Organization (API key: `dev-aims-demo-key`)
- **System:** Credit Scoring AI (high-risk, requires FRIA)
- **7 Evidences:** model_card.pdf, training_data_spec.pdf, validation_report.pdf, bias_analysis.pdf, security_audit.pdf, privacy_impact.pdf, human_oversight_sop.pdf
- **FRIA:** Submitted as applicable
- **Controls:** 3 batches (design, testing, monitoring)
- **Incident:** 1 logged incident

## Notes

- The test suite now properly isolates database state between tests
- `get_db` dependency overrides are properly restored after each test
- All datetime fields use `UTCDateTime` and return timezone-aware UTC timestamps
- Evidence endpoint is `/controls/{system_id}/evidence` (not `/systems/{system_id}/evidence`)
- Evidence schema uses `upload_date` field (not `uploaded_at`)

