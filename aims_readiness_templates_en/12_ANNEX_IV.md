---
template_id: annex_iv_v1
iso_clauses: ["Annex IV"]
ai_act: ["Annex IV"]
version: "{{ metadata.version }}"
language: "en"
generated_at: "{{ metadata.generated_at }}"
---

# Annex IV - Technical Documentation
*{{ company.name }} - {{ system.name }}*

**System:** {{ system.name }}  
**Domain:** {{ system.domain }}  
**AI Act Classification:** {{ system.ai_act_class }}  
**Generated:** {{ metadata.generated_at }}

## 1. General Information

### 1.1 System Identification
- **System Name:** {{ system.name }}
- **Purpose:** {{ system.purpose }}
- **Domain:** {{ system.domain }}
- **Deployment Context:** {{ system.deployment_context }}
- **Lifecycle Stage:** {{ system.lifecycle_stage }}
- **System Owner:** {{ system.owner_email }}

### 1.2 Organization Information
- **Organization:** {{ company.name }}
- **Primary Contact:** {{ company.primary_contact_name }} ({{ company.primary_contact_email }})
- **DPO Contact:** {{ company.dpo_contact_name }} ({{ company.dpo_contact_email }})
- **Organization Role:** {{ company.org_role }}

### 1.3 AI Act Classification
- **Risk Category:** {{ system.risk_category }}
- **AI Act Class:** {{ system.ai_act_class }}
- **High-Risk System:** {% if system.ai_act_class == 'high-risk' %}Yes{% else %}No{% endif %}
- **Requires FRIA:** {{ system.requires_fria }}

{% if system.ai_act_class == 'high-risk' %}
### 1.4 Annex III Categories
This system falls under the following high-risk AI system categories:
- Biometric identification: {{ system.uses_biometrics }}
- Biometrics in public: {{ system.biometrics_in_public }}
- General Purpose AI: {{ system.is_general_purpose_ai }}
- Fundamental rights impact: {{ system.impacts_fundamental_rights }}
{% endif %}

## 2. System Characteristics

### 2.1 Affected Users
{{ system.affected_users }}

### 2.2 Third-Party Providers
{{ system.third_party_providers }}

### 2.3 Data Processing
- **Personal Data Processed:** {{ system.personal_data_processed }}
- **Training Data Sensitivity:** {{ system.training_data_sensitivity or 'Not specified' }}
- **Output Type:** {{ system.output_type or 'Not specified' }}

## 3. Risk Assessment

{% if risks %}
### 3.1 Identified Risks
| Risk ID | Description | Likelihood | Impact | Mitigation | Owner | Status |
|---------|-------------|-----------:|-------:|------------|-------|--------|
{% for risk in risks %}
| R-{{ "%03d"|format(loop.index) }} | {{ risk.description }} | {{ risk.likelihood }} | {{ risk.impact }} | {{ risk.mitigation }} | {{ risk.owner_email }} | {{ risk.priority }} |
{% endfor %}
{% else %}
### 3.1 Identified Risks
*No risks have been identified for this system yet. Please complete the risk assessment.*
{% endif %}

## 4. Controls and Measures

{% if controls %}
### 4.1 Implemented Controls
| Control ID | Name | Status | Owner | Due Date | Evidence |
|------------|------|--------|-------|----------|----------|
{% for control in controls %}
| {{ control.iso_clause }} | {{ control.name }} | {{ control.status }} | {{ control.owner_email }} | {% if control.due_date %}{{ control.due_date }}{% else %}Not set{% endif %} | {% if control.evidence %}{% for ev in control.evidence %}{{ ev.label }}{% if not loop.last %}; {% endif %}{% endfor %}{% else %}No evidence{% endif %} |
{% endfor %}

#### Evidence Citations
{% for control in controls %}
{% if control.evidence %}
**{{ control.iso_clause }} - {{ control.name }}:**
{% for ev in control.evidence %}
- [EV-{{ ev.id }} | {{ ev.label }} | sha256:{{ ev.checksum[:16] if ev.checksum else 'N/A' }}]
{% endfor %}
{% endif %}
{% endfor %}
{% else %}
### 4.1 Implemented Controls
*No controls have been defined for this system yet. Please complete the controls assessment.*
{% endif %}

## 5. Human Oversight

### 5.1 Oversight Configuration
- **Oversight Mode:** {{ oversight.mode }}
- **Intervention Rules:** {{ oversight.intervention_rules }}
- **Manual Override:** {{ oversight.manual_override }}
- **Appeals Channel:** {{ oversight.appeals_channel }}
- **Appeals SLA:** {{ oversight.appeals_sla_days }} days

### 5.2 Training and Communication
- **Training Plan:** {{ oversight.training_plan }}
- **Communication Plan:** {{ oversight.comm_plan }}
- **Ethics Committee:** {{ oversight.ethics_committee }}

## 6. Post-Market Monitoring

### 6.1 Monitoring Configuration
- **Logging Scope:** {{ pmm.logging_scope }}
- **Retention Period:** {{ pmm.retention_months }} months
- **Drift Threshold:** {{ pmm.drift_threshold }}
- **Audit Frequency:** {{ pmm.audit_frequency }}
- **Management Review:** {{ pmm.management_review_frequency }}

### 6.2 Fairness and Performance
- **Fairness Metrics:** {{ pmm.fairness_metrics }}
- **Incident Tool:** {{ pmm.incident_tool }}
- **Improvement Plan:** {{ pmm.improvement_plan }}

### 6.3 EU Database Status
{% if pmm.eu_db_required %}
- **EU Database Required:** Yes
- **Status:** {{ pmm.eu_db_status }}
{% else %}
- **EU Database Required:** No
{% endif %}

## 7. Accuracy and Robustness

### 7.1 Model Validation
- **Validation Method:** {{ pmm.fairness_metrics }}
- **Performance Metrics:** {{ pmm.fairness_metrics }}
- **Drift Detection:** {{ pmm.drift_threshold }} threshold

### 7.2 Cybersecurity
{% if risks %}
{% for risk in risks %}
{% if 'security' in risk.description.lower() or 'cyber' in risk.description.lower() %}
- **Risk:** {{ risk.description }}
- **Mitigation:** {{ risk.mitigation }}
{% endif %}
{% endfor %}
{% else %}
*No cybersecurity risks identified.*
{% endif %}

## 8. Evidence and Documentation

{% if evidence %}
### 8.1 Evidence Register
| Evidence ID | Label | Version | Checksum | Control |
|-------------|-------|---------|----------|---------|
{% for ev in evidence %}
| EV-{{ ev.id }} | {{ ev.label }} | {{ ev.version }} | {{ ev.checksum[:16] if ev.checksum else 'N/A' }} | {{ ev.iso_clause }} |
{% endfor %}
{% else %}
### 8.1 Evidence Register
*No evidence has been uploaded for this system yet.*
{% endif %}

## 9. Change Management

### 9.1 Model Version
{% if model_version %}
- **Current Version:** {{ model_version.version }}
- **Released:** {{ model_version.released_at }}
- **Approved By:** {{ model_version.approver_email }}
- **Artifact Hash:** {{ model_version.artifact_hash }}
{% if model_version.notes %}
- **Notes:** {{ model_version.notes }}
{% endif %}
{% else %}
- **Current Version:** 1.0.0 (Initial deployment)
- **Change Management:** Version control to be implemented
{% endif %}

{% if model_versions and model_versions|length > 1 %}
### 9.2 Version History
| Version | Released | Approver | Hash |
|---------|----------|----------|------|
{% for v in model_versions %}
| {{ v.version }} | {{ v.released_at }} | {{ v.approver_email or 'N/A' }} | {{ v.artifact_hash[:16] if v.artifact_hash else 'N/A' }} |
{% endfor %}
{% endif %}

## 10. Compliance Status

### 10.1 FRIA Assessment
{% if fria %}
- **FRIA Required:** {{ system.requires_fria }}
- **FRIA Status:** {{ fria.status }}
- **Applicable:** {{ fria.applicable }}
- **Completed:** {{ fria.created_at }}
{% else %}
- **FRIA Required:** {{ system.requires_fria }}
- **FRIA Status:** Not completed
{% endif %}

### 10.2 GDPR Compliance
{% if system.personal_data_processed and system.dpia_link %}
- **DPIA Conducted:** Yes
- **DPIA Reference:** {{ system.dpia_link }}
- **Compliance:** GDPR Article 35 (Data Protection Impact Assessment)
{% elif system.personal_data_processed %}
- **DPIA Required:** Yes (sensitive personal data processing)
- **DPIA Status:** To be conducted
{% else %}
- **DPIA Required:** No (no personal data processing)
{% endif %}

### 10.3 Compliance Summary
- **Total Risks:** {{ metadata.risk_count }}
- **Total Controls:** {{ metadata.control_count }}
- **Total Evidence:** {{ metadata.evidence_count }}
- **FRIA Complete:** {{ metadata.has_fria }}

---

## Document Approval

{% if approval %}
**Status:** {{ approval.status|upper }}  
{% if approval.status == 'approved' %}
**Approved By:** {{ approval.approver_email }}  
**Approved At:** {{ approval.approved_at }}  
**Document Hash:** {{ approval.document_hash[:16] }}...
{% elif approval.status == 'submitted' %}
**Submitted By:** {{ approval.submitted_by }}  
**Submitted At:** {{ approval.submitted_at }}  
**Awaiting Approval**
{% endif %}
{% else %}
**Status:** DRAFT (Not yet submitted for review)
{% endif %}

---

**Document Generated:** {{ metadata.generated_at }}  
**System ID:** {{ metadata.system_id }}  
**Organization:** {{ company.name }}
