---
template_id: oversight_sop_v1
iso_clauses: ["B.9.3"]
ai_act: ["Annex IV §2.3"]
version: "{{ metadata.version }}"
language: "en"
generated_at: "{{ metadata.generated_at }}"
---

# Human Oversight — Standard Operating Procedure
*{{ company.name }} - {{ system.name }}*

**System:** {{ system.name }}  
**Oversight Mode:** {{ oversight.mode }}  
**Generated:** {{ metadata.generated_at }}

## Oversight Configuration

### Intervention Rules
{{ oversight.intervention_rules }}

### Manual Override
- **Enabled:** {{ oversight.manual_override }}
- **Process:** Two‑person review → decision documented → audit log updated

### Appeals Process
- **Channel:** {{ oversight.appeals_channel }}
- **SLA:** {{ oversight.appeals_sla_days }} days
- **Responsible:** {{ oversight.appeals_responsible_email }}

### Training and Communication
- **Training Plan:** {{ oversight.training_plan }}
- **Communication Plan:** {{ oversight.comm_plan }}
- **External Disclosure:** {{ oversight.external_disclosure }}

### Ethics Committee
- **Active:** {{ oversight.ethics_committee }}

## Triggers
- Borderline scores (0.45–0.55)
- Low‑confidence explanations
- Customer appeals
- High-risk decisions

## Process
Two‑person review → decision documented → audit log updated.  
KPIs: override ratio, appeal turnaround time.

## Tools
Explanation viewer; appeals portal; audit log.

**Approvals:** {{ company.dpo_contact_name }} (DPO) / {{ company.primary_contact_name }} (Governance Lead)
