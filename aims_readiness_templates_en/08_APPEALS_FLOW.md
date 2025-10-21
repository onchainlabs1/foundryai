---
template_id: appeals_flow_v1
iso_clauses: ["B.8.3"]
ai_act: ["Art. 68","FRIA"]
version: "{{ metadata.version }}"
language: "en"
generated_at: "{{ metadata.generated_at }}"
---

# Appeals & Feedback Process
*{{ company.name }} - {{ system.name }}*

## Appeals Channel

**Channel:** {{ oversight.appeals_channel }}  
**SLA:** {{ oversight.appeals_sla_days }} business days  
**Responsible:** {{ oversight.appeals_responsible_email }}

## Process

1. User submits appeal via {{ oversight.appeals_channel }} (case ID assigned)
2. Analyst reviews within {{ oversight.appeals_sla_days }} business days
3. Re-evaluation performed; rationale recorded
4. Decision communicated to user
5. Systemic issues fed into improvement backlog: {{ pmm.improvement_plan }}

## KPIs

- Time-to-close: ≤ {{ oversight.appeals_sla_days }} days
- Percentage overturned: tracked
- User satisfaction: monitored

**Audit Frequency:** {{ pmm.audit_frequency }}
