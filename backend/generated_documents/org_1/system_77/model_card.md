---
template_id: model_card_v1
iso_clauses: ["A.6.2","B.6"]
ai_act: ["Annex IV §8"]
version: "1.0.0"
language: "en"
generated_at: "2025-10-19T12:58:43.410794+00:00"
---

# Model Card — Fallback Test System v1.0

**Organization:** Test Company  
**System:** Fallback Test System  
**Domain:** testing  
**AI Act Classification:** minimal  
**Generated:** 2025-10-19T12:58:43.410794+00:00

## Overview
- Objective: Testing PDF fallback
- Algorithm: AI/ML System
- Owners: Test Company AI Team
- General Purpose AI: No
- Biometric Data: No
- Personal Data: No

## Data & Training
- Sources: <datasets, dates, jurisdictions>
- Quality: missing %, outliers, representativeness
- Bias testing: metrics and acceptance gates

## Performance
| Metric | Value | Dataset | Date |
|--------|------:|---------|------|
| AUC / Accuracy | 0.92 | Holdout 2024Q4 | 2025‑01‑10 |

## Explainability & Limitations
- Local explanations: SHAP/attribution viewer
- Known limitations: <e.g., macro shocks, covariate shift>

## Human Oversight & Change Management
- Borderline review rules; escalation path
- Versioning in MLflow; rollback policy; approvals

References: ISO 42001 A.6.2/B.6; AI Act Annex IV §8.