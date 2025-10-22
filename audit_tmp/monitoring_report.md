---
template_id: pm_monitoring_v1
iso_clauses: ["A.6.2.6","9.1"]
ai_act: ["Art. 72"]
version: "1.0.0"
language: "en"
generated_at: "2025-10-22T11:54:53.501909+00:00"
---

# Post‑Market Monitoring Report — Credit Scoring AI
*Demo Organization*

**System:** Credit Scoring AI  
**Domain:** Finance  
**Generated:** 2025-10-22T11:54:53.501909+00:00

## Monitoring Configuration

### Logging Scope
System inputs, outputs, and decisions

### Retention Policy
- **Retention Period:** 12 months
- **Drift Alert Threshold:** 10%
- **Audit Frequency:** quarterly
- **Management Review:** quarterly

### Fairness Metrics
Accuracy, precision, recall

### Incident Management
- **Tool:** Internal ticketing system
- **Improvement Plan:** Continuous improvement based on monitoring results

## EU Database Status

- **EU Database Required:** No


## Key Indicators
| KPI | Result | Target | Status | Notes |
|-----|-------:|-------:|:------:|-------|
| Drift Alerts | 1 | ≤ 2 | OK | One false positive |
| Overrides | 4.7% | ≤ 5% | OK | Within range |
| Complaints | 3 | ≤ 3 | OK | All closed |

## Actions
- Retraining scheduled <date>; threshold tuning in segment <X>  
- New subgroup fairness tests

**Approvals:** DPO (DPO) / Contact Person (Governance Lead)