---
template_id: logging_plan_v1
iso_clauses: ["A.6.2.6","A.6.2.8","9.1"]
ai_act: ["Annex IV §9"]
version: "1.0.0"
language: "en"
generated_at: "2025-10-22T11:54:53.526070+00:00"
---

# Logging & Monitoring Plan
*Demo Organization - Credit Scoring AI*

## Logging Scope

System inputs, outputs, and decisions

## Event Logging

The system logs the following events:
- Decision timestamp
- Input features hash
- Model version
- Prediction/score
- Confidence level
- Human override flag
- User interaction

**Retention Period:** 12 months

## Metrics & Alerts

| Metric | Target | Alert Threshold | Owner |
|--------|-------:|----------------:|-------|
| Data Drift (PSI) | < 10% | ≥ 10% | ana@techcorp.ai |
| Fairness Metrics | Accuracy, precision, recall | Deviation > 5% | ana@techcorp.ai |
| System Availability | > 99% | < 95% | Ops Team |

## Incident Response & Review

- **Incident Tool:** Internal ticketing system
- **Review Frequency:** quarterly
- **Audit Frequency:** quarterly
- **Improvement Plan:** Continuous improvement based on monitoring results

References: ISO 42001 A.6.2.6/A.6.2.8/§9.1; AI Act Annex IV §9; Art. 72.