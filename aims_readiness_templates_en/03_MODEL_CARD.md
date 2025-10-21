---
template_id: model_card_v1
iso_clauses: ["A.6.2","B.6"]
ai_act: ["Annex IV §8"]
version: "{{ metadata.version }}"
language: "en"
generated_at: "{{ metadata.generated_at }}"
---

# Model Card — {{ system.name }}{% if model_version %} v{{ model_version.version }}{% endif %}

**Organization:** {{ company.name }}  
**System:** {{ system.name }}  
**Domain:** {{ system.domain }}  
**AI Act Classification:** {{ system.ai_act_class }}  
**Generated:** {{ metadata.generated_at }}

## Overview
- **Objective:** {{ system.purpose }}
- **Algorithm:** AI/ML System
- **Owner:** {{ system.owner_email }}
- **Lifecycle Stage:** {{ system.lifecycle_stage }}
- **Deployment Context:** {{ system.deployment_context }}
- **General Purpose AI:** {{ "Yes" if system.is_general_purpose_ai else "No" }}
- **Biometric Data:** {{ "Yes" if system.uses_biometrics else "No" }}
- **Personal Data:** {{ "Yes" if system.personal_data_processed else "No" }}

## Data & Training

{% if system.third_party_providers %}
**Data Sources:**  
{{ system.third_party_providers }}
{% else %}
**Data Sources:** Internal training data
{% endif %}

**Quality Assurance:** Data quality checks are performed as part of the PMM process  
**Bias Testing:** Fairness metrics monitored: {{ pmm.fairness_metrics if pmm else 'Not configured' }}

## Performance

{% if model_version %}
**Current Version:** {{ model_version.version }}  
**Released:** {{ model_version.released_at }}  
**Approved By:** {{ model_version.approver_email }}  
{% if model_version.artifact_hash %}**Artifact Hash:** {{ model_version.artifact_hash[:16] }}...{% endif %}
{% else %}
*Model versioning not yet configured*
{% endif %}

**Performance Monitoring:**  
- Drift threshold: {{ pmm.drift_threshold if pmm else 'Not set' }}  
- Retention period: {{ pmm.retention_months if pmm else 'Not set' }} months  
- Review frequency: {{ pmm.management_review_frequency if pmm else 'Not set' }}

## Explainability & Limitations

**Transparency:** {{ 'Explanations provided to users' if oversight else 'Standard explanations' }}  
**Known Limitations:** {{ system.affected_users if system.affected_users else 'System limitations documented in risk assessment' }}

{% if risks %}
**Identified Limitations:**
{% for risk in risks %}
- {{ risk.description }} (Impact: {{ risk.impact }}, Likelihood: {{ risk.likelihood }})
{% endfor %}
{% endif %}

## Human Oversight & Change Management

{% if oversight %}
**Oversight Mode:** {{ oversight.mode }}  
**Review Trigger:** {{ oversight.review_trigger }}  
**Override Rights:** {{ 'Enabled' if oversight.override_rights else 'Not configured' }}  
**Intervention Rules:** {{ oversight.intervention_rules }}
{% else %}
*Human oversight not configured*
{% endif %}

**Version Control:** {{ 'Model versions tracked' if model_versions else 'Not yet implemented' }}  
**Rollback Policy:** Rollback to previous version if performance degrades beyond thresholds

{% if model_versions %}
**Version History:**
{% for v in model_versions[:5] %}
- v{{ v.version }} — {{ v.released_at }} — {{ v.approver_email }}
{% endfor %}
{% endif %}

---

**References:** ISO 42001 A.6.2/B.6; AI Act Annex IV §8.
