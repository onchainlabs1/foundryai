---
template_id: audit_log_v1
iso_clauses: ["9","10"]
ai_act: ["Annex IV §9"]
version: "{{ metadata.version }}"
language: "en"
generated_at: "{{ metadata.generated_at }}"
---

# Internal Audit & Improvement Log — {{ system.name }}

**Organization:** {{ company.name }}  
**System:** {{ system.name }}  
**Generated:** {{ metadata.generated_at }}

## Audit Schedule

**Audit Frequency:** {{ pmm.audit_frequency if pmm else 'Quarterly' }}  
**Management Review Frequency:** {{ pmm.management_review_frequency if pmm else 'Semi-annual' }}  
**Improvement Plan:** {{ pmm.improvement_plan if pmm else 'Continuous improvement process' }}

## Recent Audits

| Date | Area | Auditor | Findings | Status |
|------|------|---------|----------|--------|
| {{ metadata.generated_at }} | System Documentation | {{ system.owner_email }} | Initial documentation complete | In Progress |
{% if controls %}{% for control in controls[:3] %}
| {{ metadata.generated_at }} | {{ control.control_name }} | {{ control.owner_email }} | {{ control.status }} | {{ control.status|title }} |
{% endfor %}{% endif %}

## Corrective Actions

{% if pmm and pmm.improvement_plan %}
**Improvement Plan:**  
{{ pmm.improvement_plan }}
{% else %}
Corrective actions tracked and managed according to audit findings.
{% endif %}

## Next Review

**Next Management Review:** Based on {{ pmm.management_review_frequency if pmm else 'annual schedule' }}  
**Next Audit:** Based on {{ pmm.audit_frequency if pmm else 'quarterly schedule' }}

---

**Contact:** {{ system.owner_email }}  
**Incident Tool:** {{ pmm.incident_tool if pmm else 'Standard incident management' }}
