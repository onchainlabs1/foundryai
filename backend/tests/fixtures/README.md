# Test Fixtures

This directory contains test fixtures and golden data for the AIMS Readiness platform.

## Golden ZIP: Credit Scoring AI

- **Scenario:** Medium complexity
- **Files:** 7 evidence documents + FRIA + controls + 1 incident
- **Regenerate:** `python generate_golden_zip.py`
- **Checksums:** See `checksums.txt`

### Scenario Details

The Credit Scoring AI scenario represents a realistic high-risk AI system used for automated creditworthiness assessment in the finance domain.

**System Characteristics:**
- **Name:** Credit Scoring AI
- **Purpose:** Automated creditworthiness assessment
- **Domain:** Finance
- **AI Act Class:** High-risk
- **Role:** Provider
- **FRIA Required:** Yes

**Evidence Documents (7 files):**
1. `model_card.pdf` - ML model documentation
2. `training_data_spec.pdf` - Dataset specification
3. `validation_report.pdf` - Model validation results
4. `bias_analysis.pdf` - Fairness assessment
5. `security_audit.pdf` - Security review
6. `privacy_impact.pdf` - DPIA results
7. `human_oversight_sop.pdf` - Human review procedures

**Controls (3 controls):**
- ISO42001:6.1 (High priority, Implemented)
- ISO42001:6.2 (High priority, Implemented)
- ISO42001:7.1 (Medium priority, In progress)

**Incident:**
- Severity: Medium
- Description: Model drift detected in production
- Status: Resolved
- Corrective action: Retrained model with recent data

**FRIA Assessment:**
- Applicable: Yes
- Biometric data: No
- Fundamental rights: Yes
- Critical infrastructure: No
- Vulnerable groups: Yes
- High-risk area: Yes

## Usage in Tests

```python
from tests.fixtures.credit_scoring_ai import load_scenario, seed_full_system

# Load scenario data
scenario = load_scenario()

# Seed a complete system
system_id = seed_full_system(db, org_id)
```

## Regenerating the Golden ZIP

To regenerate the golden ZIP file with fresh data:

```bash
cd backend/tests/fixtures
python generate_golden_zip.py
```

This will:
1. Create a new system with the Credit Scoring AI scenario
2. Upload all evidence files
3. Submit FRIA assessment
4. Create controls
5. Log incident
6. Export Annex IV ZIP
7. Save as `credit_scoring_ai.zip`
8. Generate checksums in `checksums.txt`

## File Structure

```
fixtures/
├── README.md                    # This file
├── credit_scoring_ai.json      # Scenario data
├── credit_scoring_ai.zip       # Golden ZIP file
├── checksums.txt               # File checksums
├── generate_golden_zip.py      # Generation script
├── credit_scoring_ai.py        # Helper functions
└── __init__.py                 # Package init
```

## Testing with Golden ZIP

The golden ZIP can be used to test:

1. **Manifest Schema Validation (T1)** - Verify manifest.json structure
2. **ZIP Completeness (T2)** - Check all required documents are present
3. **Placeholder Detection (T3)** - Scan for incomplete content
4. **Evidence Citations (T4)** - Verify evidence references
5. **SoA Contract (T5)** - Validate Statement of Applicability
6. **FRIA Gate (T6)** - Test FRIA requirement enforcement
7. **Blocking Issues (T7)** - Check blocking issues service
8. **AI Act Badges (T8)** - Validate AI Act metadata

## Checksums

The `checksums.txt` file contains SHA256 hashes and file sizes for verification:

```
credit_scoring_ai.zip:
  SHA256: abc123...
  Size: 12345 bytes
```

Use these checksums to verify file integrity in tests.
