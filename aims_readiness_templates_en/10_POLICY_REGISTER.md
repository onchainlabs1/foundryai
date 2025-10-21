---
template_id: policy_register_v1
iso_clauses: ["4","5","7.5"]
ai_act: ["Annex IV §2"]
version: "{{ metadata.version }}"
language: "en"
generated_at: "{{ metadata.generated_at }}"
---

# Policy Register — {{ company.name }}

**System:** {{ system.name }}  
**Generated:** {{ metadata.generated_at }}

| Policy | Objective | Owner | Review Frequency |
|--------|-----------|-------|------------------|
| AI Governance Policy | Define scope, roles, objectives | {{ company.contact_email }} | {{ pmm.management_review_frequency if pmm else 'Annual' }} |
| Data Protection Policy | GDPR alignment | {{ company.contact_email }} | {{ pmm.audit_frequency if pmm else 'Annual' }} |
| AI Ethics Guidelines | Responsible AI principles | {{ system.owner_email }} | {{ pmm.management_review_frequency if pmm else 'Annual' }} |
| Human Oversight Policy | Define oversight procedures | {{ oversight.appeals_responsible_email if oversight else system.owner_email }} | {{ pmm.management_review_frequency if pmm else 'Semi-annual' }} |
| Post-Market Monitoring Policy | Continuous monitoring procedures | {{ system.owner_email }} | {{ pmm.audit_frequency if pmm else 'Quarterly' }} |

**Organization Role:** {{ company.org_role }}  
**Contact:** {{ company.contact_email }}
