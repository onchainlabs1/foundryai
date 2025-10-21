---
template_id: fria_v1
iso_clauses: ["6.1.4"]
ai_act: ["Art. 27", "Annex IV §2"]
version: "{{ metadata.version }}"
language: "en"
generated_at: "{{ metadata.generated_at }}"
---

# Fundamental Rights Impact Assessment (FRIA)

**System:** {{ system.name }}  
**Organization:** {{ company.name }}  
**Assessment Date:** {{ metadata.generated_at }}

---

{% if approval %}
## Document Approval

**Status:** {{ approval.status|upper }}  
{% if approval.status == 'approved' %}
**Approved By:** {{ approval.approver_email }}  
**Approved At:** {{ approval.approved_at }}  
**Document Hash:** {{ approval.document_hash[:16] if approval.document_hash else 'N/A' }}...
{% elif approval.status == 'submitted' %}
**Submitted By:** {{ approval.submitted_by }}  
**Submitted At:** {{ approval.submitted_at }}  
**Awaiting Approval**
{% endif %}
{% else %}
**Status:** DRAFT (Not yet submitted for review)
{% endif %}

---

## 1. Executive Summary

{% if fria %}
**Applicable:** {{ 'Yes' if fria.applicable else 'No' }}  
**Status:** {{ fria.status }}  
{% if fria.proportionality %}**Proportionality:** {{ fria.proportionality }}{% endif %}  
{% if fria.residual_risk %}**Residual Risk:** {{ fria.residual_risk }}{% endif %}
{% else %}
*FRIA assessment not yet completed.*
{% endif %}

## 2. System Context

**System Name:** {{ system.name }}  
**Purpose:** {{ system.purpose }}  
**Domain:** {{ system.domain }}  
**Deployment Context:** {{ system.deployment_context }}  
**Lifecycle Stage:** {{ system.lifecycle_stage }}

**AI Act Classification:** {{ system.ai_act_class }}  
**Personal Data Processed:** {{ 'Yes' if system.personal_data_processed else 'No' }}  
**Impacts Fundamental Rights:** {{ 'Yes' if system.impacts_fundamental_rights else 'No' }}

**Affected Users:** {{ system.affected_users or 'Not specified' }}

{% if system.third_party_providers %}
**Third-Party Providers/Data Sources:**  
{{ system.third_party_providers }}
{% endif %}

## 3. Fundamental Rights Analysis

{% if fria and fria.risks_json %}
### 3.1 Identified Risks to Fundamental Rights

{{ fria.risks_json }}

{% else %}
### 3.1 General Risk Assessment

{% if risks %}
| Risk ID | Description | Impact | Likelihood | Mitigation |
|---------|-------------|--------|-----------|------------|
{% for risk in risks %}
| R-{{ risk.id }} | {{ risk.description }} | {{ risk.impact }} | {{ risk.likelihood }} | {{ risk.mitigation }} |
{% endfor %}
{% else %}
*No risks documented. Please complete risk assessment.*
{% endif %}
{% endif %}

## 4. Stakeholder Consultation

**Consultation Method:** Internal review and stakeholder engagement  
**Date:** {{ metadata.generated_at }}  
**Participants:** 
- System Owner: {{ system.owner_email }}
- Organization: {{ company.name }}

{% if fria and fria.review_notes %}
**Review Notes:**  
{{ fria.review_notes }}
{% endif %}

## 5. Safeguards and Mitigation Measures

{% if fria and fria.safeguards_json %}
{{ fria.safeguards_json }}
{% else %}
### 5.1 Technical Safeguards

{% if controls %}
| Control ID | Control Name | Status | Owner | Due Date |
|-----------|--------------|--------|-------|----------|
{% for control in controls %}
| {{ control.iso_clause }} | {{ control.control_name }} | {{ control.status }} | {{ control.owner_email }} | {% if control.due_date %}{{ control.due_date }}{% else %}Not set{% endif %} |
{% endfor %}
{% else %}
*No controls documented. Please complete controls assessment.*
{% endif %}
{% endif %}

## 6. Human Oversight

{% if oversight %}
**Oversight Mode:** {{ oversight.mode }}  
**Review Trigger:** {{ oversight.review_trigger }}  
**Override Rights:** {{ 'Yes' if oversight.override_rights else 'No' }}  
**Intervention Rules:** {{ oversight.intervention_rules }}  
**Appeals Channel:** {{ oversight.appeals_channel }}  
**Appeals SLA:** {{ oversight.appeals_sla_days }} business days
{% else %}
*Human oversight configuration not completed.*
{% endif %}

## 7. Proportionality Assessment

{% if fria and fria.proportionality %}
{{ fria.proportionality }}
{% else %}
The safeguards and mitigation measures are proportionate to the identified risks and fundamental rights impacts. The system includes:

- Human oversight mechanisms ({{ oversight.mode if oversight else 'not configured' }})
- Transparency measures (explanations, notifications)
- Data minimization and security controls
- Regular monitoring and review processes
{% endif %}

## 8. Residual Risk

{% if fria and fria.residual_risk %}
**Assessment:** {{ fria.residual_risk }}
{% else %}
**Assessment:** After implementing all safeguards and mitigation measures, residual risks remain within acceptable tolerance levels. Continuous monitoring is in place to detect and address emerging risks.
{% endif %}

## 9. Data Protection Impact Assessment (DPIA)

{% if system.personal_data_processed %}
**DPIA Required:** Yes  
{% if system.dpia_link %}
**DPIA Reference:** {{ system.dpia_link }}
{% elif fria and fria.dpia_reference %}
**DPIA Reference:** {{ fria.dpia_reference }}
{% else %}
**DPIA Status:** Pending completion
{% endif %}

**Alignment:** This FRIA is conducted in alignment with the DPIA to ensure comprehensive assessment of both data protection and fundamental rights impacts.
{% else %}
**DPIA Required:** No (system does not process personal data)
{% endif %}

## 10. Re-assessment Triggers

The FRIA shall be reviewed and updated when:

1. Significant changes to the AI system (model updates, new features)
2. Changes in deployment context or affected user groups
3. New risks or impacts are identified
4. Regulatory requirements change
5. At least annually, or as determined by: {{ pmm.management_review_frequency if pmm else 'Annual review schedule' }}

## 11. Decision and Approval

{% if fria %}
**FRIA Completed:** {{ fria.created_at if fria.created_at else metadata.generated_at }}  
**Justification:** {{ fria.justification if fria.justification else 'Assessment completed as required by EU AI Act Article 27' }}
{% endif %}

{% if approval and approval.status == 'approved' %}
**Final Approval:**  
Approved by {{ approval.approver_email }} on {{ approval.approved_at }}
{% else %}
*Pending final approval*
{% endif %}

## 12. References

- **EU AI Act:** Article 27 (Fundamental Rights Impact Assessment)
- **ISO/IEC 42001:** §6.1.4 (Actions to address risks and opportunities)
- **GDPR:** Article 35 (Data Protection Impact Assessment)
- **Charter of Fundamental Rights of the European Union**

---

**Document ID:** FRIA-{{ system.id }}  
**Generated:** {{ metadata.generated_at }}  
**Organization:** {{ company.name }}  
**System:** {{ system.name }}
