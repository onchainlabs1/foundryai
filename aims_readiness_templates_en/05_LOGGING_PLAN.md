---
template_id: logging_plan_v1
iso_clauses: ["A.6.2.6","A.6.2.8","9.1"]
ai_act: ["Annex IV §9"]
version: "1.0.0"
language: "en"
generated_at: "2025-10-17T08:42:56Z"
---

# Logging & Monitoring Plan

## Event Logging (minimum)
- Decision timestamp, input hash, model version, score, explanation ref, override flag

## Metrics & Alerts
| Metric | Target | Alert | Owner |
|--------|-------:|------:|-------|
| Data Drift (PSI) | < 0.10 | ≥ 0.15 | MLOps |
| Fairness Gap | ≤ 5% | ≥ 8% | ML Lead |
| Error Rate | < 2% | ≥ 5% | Ops |

## Incident Response & Review
- Incident register; CAPA workflow; quarterly management review.

References: ISO 42001 A.6.2.6/A.6.2.8/§9.1; AI Act Annex IV §9; Art. 72.
