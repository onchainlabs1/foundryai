---
template_id: transparency_notice_gpai_v1
iso_clauses: ["B.9.3"]
ai_act: ["Art. 13", "Art. 52"]
version: "{{ metadata.version }}"
language: "en"
generated_at: "{{ metadata.generated_at }}"
---

# Transparency Notice - General Purpose AI
*{{ company.name }} - {{ system.name }}*

**System:** {{ system.name }}  
**Generated:** {{ metadata.generated_at }}

---

## Notice to Users

This system uses **General Purpose AI** technology. This transparency notice explains how AI-generated content is identified and how users are informed about AI system use.

---

## 1. AI System Identification

### 1.1 System Information
- **System Name:** {{ system.name }}
- **Purpose:** {{ system.purpose }}
- **Domain:** {{ system.domain }}
- **AI Technology:** General Purpose AI (GPAI)

### 1.2 Provider Information
- **Organization:** {{ company.name }}
- **Contact:** {{ company.primary_contact_email }}
- **DPO:** {{ company.dpo_contact_email }}

---

## 2. User Notification

### 2.1 How Users Are Informed

Users interacting with this system are informed that they are interacting with an AI system through:

1. **Clear Labeling:** All AI-generated outputs are labeled with "🤖 AI-Generated" or equivalent indicator
2. **Initial Disclosure:** Users receive notification upon first interaction that the system uses AI
3. **Interface Indicators:** Visual indicators throughout the user interface
4. **Documentation:** This transparency notice and instructions for use

### 2.2 Notification Methods

- **Primary:** In-application banner or label on all AI outputs
- **Secondary:** Email notification at account creation/first use
- **Tertiary:** Terms of service and privacy policy disclosure

---

## 3. AI Output Labeling

### 3.1 Labeling Requirements

All outputs from this GPAI system are labeled to indicate:

1. **AI-Generated Content:** Clear indication that content was produced by AI
2. **Confidence Level:** Where applicable, confidence scores or uncertainty indicators
3. **Human Review Status:** Whether output has been reviewed by a human

### 3.2 Labeling Examples

**Text Outputs:**
```
🤖 AI-Generated Response
[Content here]
Confidence: 0.87 | Human Reviewed: Yes
```

**Decisions/Recommendations:**
```
⚡ AI Recommendation
[Recommendation here]
Human Override Available | Last Review: [Date]
```

---

## 4. Capabilities and Limitations

### 4.1 What the AI Can Do

- {{ system.purpose }}
- Process inputs in domain: {{ system.domain }}
- Operate in context: {{ system.deployment_context }}

### 4.2 Known Limitations

{% if risks %}
Users should be aware of the following limitations:

{% for risk in risks %}
- **{{ risk.description }}** (Mitigation: {{ risk.mitigation }})
{% endfor %}
{% else %}
Refer to the Instructions for Use document for detailed limitations.
{% endif %}

### 4.3 When NOT to Rely Solely on AI

Users should NOT rely solely on AI outputs when:

1. Decisions have significant legal or financial consequences
2. Fundamental rights may be affected
3. Personal safety or security is at stake
4. The system indicates low confidence (< 0.7)
5. Edge cases or unusual scenarios are present

---

## 5. Human Oversight

### 5.1 Oversight Mode
**{{ oversight.mode }}**

### 5.2 Intervention Rules
{{ oversight.intervention_rules }}

### 5.3 Manual Override
- **Available:** {{ oversight.manual_override }}
- **Process:** Users can override AI decisions through designated interface
- **Documentation:** All overrides are logged and reviewed

---

## 6. Data Processing Information

### 6.1 Personal Data
{% if system.personal_data_processed %}
**This system processes personal data.**

Users and data subjects have rights under GDPR:
- Right to access
- Right to rectification
- Right to erasure
- Right to restrict processing
- Right to data portability
- Right to object
- Right not to be subject to automated decision-making (Art. 22)

Contact the DPO for data subject rights requests: {{ company.dpo_contact_email }}
{% else %}
This system does not process personal data.
{% endif %}

### 6.2 Data Retention
- **Retention Period:** {{ pmm.retention_months }} months
- **Purpose:** Legal compliance, model improvement, audit trail

---

## 7. Accuracy and Performance

### 7.1 Performance Monitoring
This system is continuously monitored for:
- {{ pmm.fairness_metrics }}
- Performance drift (threshold: {{ pmm.drift_threshold }})
- Bias and fairness across demographic groups

### 7.2 Audit Frequency
**{{ pmm.audit_frequency }}** - Regular audits ensure system performance and compliance

---

## 8. Appeals and Complaints

### 8.1 How to Appeal AI Decisions

If you disagree with an AI-generated decision:

1. **Submit Appeal:** {{ oversight.appeals_channel }}
2. **Response Time:** {{ oversight.appeals_sla_days }} business days
3. **Human Review:** All appeals reviewed by qualified human personnel
4. **Responsible Party:** {{ oversight.appeals_responsible_email }}

### 8.2 Complaint Process

For complaints about the AI system:

1. Contact: {{ company.primary_contact_email }}
2. DPO: {{ company.dpo_contact_email }}
3. External: National data protection authority (if GDPR-related)

---

## 9. Updates and Changes

### 9.1 System Updates

Users will be notified of significant system changes through:
- Email notification
- In-application banner
- Updated documentation

### 9.2 Transparency Notice Updates

This transparency notice is reviewed:
- **Frequency:** {{ pmm.management_review_frequency }}
- **Next Review:** Calculated based on deployment date

---

## 10. Regulatory Compliance

### 10.1 EU AI Act
- **Classification:** {{ system.ai_act_class }}
- **Transparency Requirements:** Article 13, Article 52
- **Provider:** {{ company.name }}
{% if system.eu_db_status == 'registered' %}
- **EU Database:** Registered
{% endif %}

### 10.2 GDPR Compliance
{% if system.personal_data_processed %}
This system complies with GDPR requirements for automated decision-making and profiling.
{% endif %}

---

**For Questions or Concerns:**
- **Primary Contact:** {{ company.primary_contact_name }} ({{ company.primary_contact_email }})
- **DPO:** {{ company.dpo_contact_name }} ({{ company.dpo_contact_email }})

---

*This transparency notice is provided in accordance with EU AI Act Article 13 and Article 52 (Transparency obligations for certain AI systems).*

**Document Version:** {{ metadata.version }}  
**Last Updated:** {{ metadata.generated_at }}
