---
template_id: model_card_v1
iso_clauses: ["A.6.2","B.6"]
ai_act: ["Annex IV §8"]
version: "{{ version }}"
language: "en"
generated_at: "{{ generated_at }}"
---

# Model Card — {{ system.name }} v1.0

**Organization:** {{ company_name }}  
**System:** {{ system.name }}  
**Domain:** {{ system_domain }}  
**AI Act Classification:** {{ ai_act_classification }}  
**Generated:** {{ generated_at }}

## Overview
- Objective: {{ system_purpose }}
- Algorithm: AI/ML System
- Owners: {{ company_name }} AI Team
- General Purpose AI: {{ "Yes" if is_gpai else "No" }}
- Biometric Data: {{ "Yes" if uses_biometrics else "No" }}
- Personal Data: {{ "Yes" if personal_data else "No" }}

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
