---
template_id: instructions_for_use_v1
iso_clauses: ["Annex IV §1"]
ai_act: ["Art. 13", "Annex IV §1"]
version: "{{ metadata.version }}"
language: "en"
generated_at: "{{ metadata.generated_at }}"
---

# Instructions for Use
*{{ company.name }} - {{ system.name }}*

**System:** {{ system.name }}  
**Version:** {{ metadata.version }}  
**Generated:** {{ metadata.generated_at }}

---

## 1. Intended Purpose

### 1.1 System Purpose
{{ system.purpose }}

### 1.2 Domain
{{ system.domain }}

### 1.3 Deployment Context
{{ system.deployment_context }}

### 1.4 Target Users
{{ system.affected_users }}

---

## 2. User Responsibilities

### 2.1 Human Oversight Requirements
{{ oversight.intervention_rules }}

### 2.2 Decision Authority
- **Oversight Mode:** {{ oversight.mode }}
- **Manual Override Enabled:** {{ oversight.manual_override }}

Users must:
1. Review system outputs in accordance with oversight mode ({{ oversight.mode }})
2. Document all manual interventions and overrides
3. Follow intervention rules for critical decisions
4. Escalate concerns through proper channels

### 2.3 Training Requirements
{{ oversight.training_plan }}

---

## 3. System Limitations

### 3.1 Known Limitations

{% if risks %}
The system has the following identified limitations and risk factors:

{% for risk in risks %}
{% if risk.residual_risk in ['Medium', 'High'] %}
#### {{ loop.index }}. {{ risk.description }}
- **Residual Risk:** {{ risk.residual_risk }}
- **Mitigation:** {{ risk.mitigation }}
- **Owner:** {{ risk.owner_email }}
{% endif %}
{% endfor %}
{% else %}
No specific limitations have been documented. Users should exercise caution and follow general best practices.
{% endif %}

### 3.2 Use Restrictions

{% if system.ai_act_class == 'high-risk' %}
**⚠️ HIGH-RISK AI SYSTEM WARNING:**

This system is classified as high-risk under the EU AI Act. Users must:
- Complete mandatory training before use
- Follow all intervention rules without exception
- Document all decisions and overrides
- Report any anomalies or concerns immediately
{% endif %}

{% if system.personal_data_processed %}
**🔒 PERSONAL DATA PROCESSING:**

This system processes personal data. Users must:
- Comply with GDPR and data protection requirements
- Obtain necessary consent where required
- Respect data subject rights (access, deletion, portability)
- Follow data retention policies ({{ pmm.retention_months }} months)
{% endif %}

{% if system.impacts_fundamental_rights %}
**⚖️ FUNDAMENTAL RIGHTS IMPACT:**

This system may impact fundamental rights. Users must:
- Complete Fundamental Rights Impact Assessment (FRIA) review
- Apply heightened scrutiny to decisions
- Provide clear explanation and appeal mechanisms
- Monitor for discriminatory outcomes
{% endif %}

---

## 4. Warnings and Precautions

### 4.1 Critical Warnings

{% if system.uses_biometrics %}
⚠️ **BIOMETRIC DATA:** This system processes biometric data. Users must obtain explicit consent and follow Art. 9 GDPR requirements.
{% endif %}

{% if system.uses_gpai %}
⚠️ **GENERAL PURPOSE AI:** This system uses general purpose AI models. Users must review outputs for accuracy and appropriateness before use.
{% endif %}

### 4.2 Operational Precautions

1. **Data Quality:** Ensure input data meets quality standards
2. **Model Drift:** Monitor for performance degradation (threshold: {{ pmm.drift_threshold }})
3. **Fairness:** Review decisions for fairness using metrics: {{ pmm.fairness_metrics }}
4. **Security:** Follow information security policies and access controls

### 4.3 Appeals and Complaints

Users and affected individuals can submit appeals or complaints through:
- **Channel:** {{ oversight.appeals_channel }}
- **SLA:** {{ oversight.appeals_sla_days }} days
- **Responsible:** {{ oversight.appeals_responsible_email }}

---

## 5. Monitoring and Logging

### 5.1 What is Logged
{{ pmm.logging_scope }}

### 5.2 Data Retention
Logs and decision data are retained for **{{ pmm.retention_months }} months** in accordance with:
- Legal requirements
- Business needs
- Data protection policies

### 5.3 Audit Frequency
This system undergoes **{{ pmm.audit_frequency }}** audits to ensure compliance and performance.

---

## 6. Incident Reporting

### 6.1 Incident Management
- **Tool:** {{ pmm.incident_tool }}
- **Responsible:** {{ system.owner_email }}

Users must report incidents immediately through the designated incident management tool.

### 6.2 Improvement Process
{{ pmm.improvement_plan }}

---

## 7. Compliance and Regulatory Information

### 7.1 EU AI Act Compliance
- **Risk Classification:** {{ system.ai_act_class }}
- **FRIA Required:** {{ system.requires_fria }}
{% if system.eu_db_status %}
- **EU Database Status:** {{ system.eu_db_status }}
{% endif %}

### 7.2 ISO/IEC 42001 Compliance
This system is managed under ISO/IEC 42001 AI Management System with:
- Risk management framework
- Controls documented in Statement of Applicability
- Continuous monitoring and improvement

---

## 8. Contact Information

### 8.1 System Owner
- **Name:** System Owner
- **Email:** {{ system.owner_email }}

### 8.2 Data Protection Officer
- **Name:** {{ company.dpo_contact_name }}
- **Email:** {{ company.dpo_contact_email }}

### 8.3 Compliance Contact
- **Name:** {{ company.primary_contact_name }}
- **Email:** {{ company.primary_contact_email }}

---

**Document Version:** {{ metadata.version }}  
**Last Updated:** {{ metadata.generated_at }}  
**Organization:** {{ company.name }}

---

*This document must be provided to all users of the AI system and reviewed annually or upon significant system changes.*
