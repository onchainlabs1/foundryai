---
template_id: pm_monitoring_v1
iso_clauses: ["A.6.2.6","9.1"]
ai_act: ["Art. 72"]
version: "{{ metadata.version }}"
language: "en"
generated_at: "{{ metadata.generated_at }}"
---

# Post‑Market Monitoring Report — {{ system.name }}
*{{ company.name }}*

**System:** {{ system.name }}  
**Domain:** {{ system.domain }}  
**Generated:** {{ metadata.generated_at }}

## Monitoring Configuration

### Logging Scope
{{ pmm.logging_scope }}

### Retention Policy
- **Retention Period:** {{ pmm.retention_months }} months
- **Drift Alert Threshold:** {{ pmm.drift_threshold }}
- **Audit Frequency:** {{ pmm.audit_frequency }}
- **Management Review:** {{ pmm.management_review_frequency }}

### Fairness Metrics
{{ pmm.fairness_metrics }}

### Incident Management
- **Tool:** {{ pmm.incident_tool }}
- **Improvement Plan:** {{ pmm.improvement_plan }}

## EU Database Status
{% if pmm.eu_db_required %}
- **EU Database Required:** Yes
- **Status:** {{ pmm.eu_db_status }}
{% else %}
- **EU Database Required:** No
{% endif %}

## Key Indicators
| KPI | Result | Target | Status | Notes |
|-----|-------:|-------:|:------:|-------|
| Drift Alerts | 1 | ≤ 2 | OK | One false positive |
| Overrides | 4.7% | ≤ 5% | OK | Within range |
| Complaints | 3 | ≤ 3 | OK | All closed |

## Actions
- Retraining scheduled <date>; threshold tuning in segment <X>  
- New subgroup fairness tests

**Approvals:** {{ company.dpo_contact_name }} (DPO) / {{ company.primary_contact_name }} (Governance Lead)
