---
template_id: impact_assessment_v1
iso_clauses: ["6.1.4"]
ai_act: ["Art. 27","Annex IV §2"]
version: "{{ metadata.version }}"
language: "en"
generated_at: "{{ metadata.generated_at }}"
---

# Fundamental Rights Impact Assessment (FRIA)
*{{ company.name }} - {{ system.name }}*

## 1. Context & Intended Use

**System:** {{ system.name }}  
**Purpose:** {{ system.purpose }}  
**Domain:** {{ system.domain }}  
**Affected Users:** {{ system.affected_users }}  
**Deployment Context:** {{ system.deployment_context }}

## 2. Impact Topics & Mitigations

{% if risks %}
| Topic | Description | Impact | Mitigation | Owner |
|------|-------------|:-----:|------------|-------|
{% for risk in risks %}
| {{ risk.description[:30] }} | {{ risk.description }} | {{ risk.impact }} | {{ risk.mitigation }} | {{ risk.owner_email }} |
{% endfor %}
{% else %}
*No risks documented. Please complete risk assessment.*
{% endif %}

## 3. Decision & Follow‑up

{% if fria %}
**FRIA Status:** {{ fria.status }}  
**Applicable:** {{ fria.applicable }}  
{% if fria.proportionality %}**Proportionality:** {{ fria.proportionality }}{% endif %}  
{% if fria.residual_risk %}**Residual Risk:** {{ fria.residual_risk }}{% endif %}
{% else %}
*FRIA assessment pending*
{% endif %}

## 4. References  
ISO/IEC 42001 §6.1.4; EU AI Act Art. 27; Annex IV §2.
