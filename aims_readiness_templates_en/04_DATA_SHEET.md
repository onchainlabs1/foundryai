---
template_id: data_sheet_v1
iso_clauses: ["A.7","B.7"]
ai_act: ["Annex IV §8.4"]
version: "{{ metadata.version }}"
language: "en"
generated_at: "{{ metadata.generated_at }}"
---

# Data Sheet — {{ system.name }}

**Organization:** {{ company.name }}  
**System:** {{ system.name }}  
**Generated:** {{ metadata.generated_at }}

## Sources & Provenance

{% if system.third_party_providers %}
**Data Sources:**  
{{ system.third_party_providers }}
{% else %}
**Data Sources:** Internal records and training data
{% endif %}

**Provenance:** Data collected and maintained by {{ company.name }}  
**Retention Policy:** {{ pmm.retention_months if pmm else 'Not configured' }} months

## Quality & Preparation

**Quality Assurance:** Data quality checks performed prior to training  
**Missing Value Handling:** Standard imputation techniques applied  
**Outlier Policy:** Statistical outlier detection and handling  
**Labelling:** {{ 'Supervised learning with labeled data' if system.lifecycle_stage == 'production' else 'Data labeling in progress' }}

**Logging:** {{ pmm.logging_scope if pmm else 'Standard logging practices' }}

## Governance & Privacy

**Personal Data Processed:** {{ 'Yes' if system.personal_data_processed else 'No' }}

{% if system.personal_data_processed %}
**Lawful Basis:** Legitimate business interest / Consent / Contract performance  
**DPIA Status:** {{ system.dpia_status|title if system.dpia_status else 'Not specified' }}
{% if system.dpia_link %}**DPIA Link:** {{ system.dpia_link }}{% endif %}  
**Access Controls:** Role-based access control (RBAC)  
**Retention:** {{ pmm.retention_months if pmm else '36' }} months
{% else %}
**Privacy Impact:** No personal data processed
**DPIA Status:** Not applicable
{% endif %}

## Representativeness & Bias

**Fairness Metrics:** {{ pmm.fairness_metrics if pmm else 'Standard fairness monitoring' }}  
**Demographic Balance:** Monitored for representativeness  
**Subgroup Coverage:** All affected user groups included  
**Monitoring Plan:** {{ pmm.management_review_frequency if pmm else 'Quarterly review' }}

{% if risks %}
**Identified Data Risks:**
{% for risk in risks %}
{% if 'data' in risk.description.lower() or 'bias' in risk.description.lower() %}
- {{ risk.description }} ({{ risk.impact }})
{% endif %}
{% endfor %}
{% endif %}

---

**References:** ISO 42001 A.7/B.7; AI Act Annex IV §8.4.
