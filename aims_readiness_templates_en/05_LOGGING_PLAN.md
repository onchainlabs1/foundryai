---
template_id: logging_plan_v1
iso_clauses: ["A.6.2.6","A.6.2.8","9.1"]
ai_act: ["Annex IV §9"]
version: "{{ metadata.version }}"
language: "en"
generated_at: "{{ metadata.generated_at }}"
---

# Logging & Monitoring Plan
*{{ company.name }} - {{ system.name }}*

## Logging Scope

{{ pmm.logging_scope }}

## Event Logging

The system logs the following events:
- Decision timestamp
- Input features hash
- Model version
- Prediction/score
- Confidence level
- Human override flag
- User interaction

**Retention Period:** {{ pmm.retention_months }} months

## Metrics & Alerts

| Metric | Target | Alert Threshold | Owner |
|--------|-------:|----------------:|-------|
| Data Drift (PSI) | < {{ pmm.drift_threshold }} | ≥ {{ pmm.drift_threshold }} | {{ system.owner_email }} |
| Fairness Metrics | {{ pmm.fairness_metrics }} | Deviation > 5% | {{ system.owner_email }} |
| System Availability | > 99% | < 95% | Ops Team |

## Incident Response & Review

- **Incident Tool:** {{ pmm.incident_tool }}
- **Review Frequency:** {{ pmm.management_review_frequency }}
- **Audit Frequency:** {{ pmm.audit_frequency }}
- **Improvement Plan:** {{ pmm.improvement_plan }}

References: ISO 42001 A.6.2.6/A.6.2.8/§9.1; AI Act Annex IV §9; Art. 72.
