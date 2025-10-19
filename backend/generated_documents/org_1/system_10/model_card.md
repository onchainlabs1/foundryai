---
template_id: model_card_v1
iso_clauses: ["A.6.2","B.6"]
ai_act: ["Annex IV §8"]
version: "1.0.0"
language: "en"
generated_at: "2025-10-19T12:39:31.564098+00:00"
---

# Model Card — No LocalStorage System v1.0

**Organization:** AIMS Demo Corporation  
**System:** No LocalStorage System  
**Domain:** testing  
**AI Act Classification:** minimal  
**Generated:** 2025-10-19T12:39:31.564098+00:00

## Overview
- Objective: Testing no localStorage dependency
- Algorithm: AI/ML System
- Owners: AIMS Demo Corporation AI Team
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