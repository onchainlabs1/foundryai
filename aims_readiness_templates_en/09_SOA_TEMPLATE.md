---
template_id: soa_template_v1
iso_clauses: ["3.26","6.1.3(f)","Annex A"]
ai_act: ["Annex IV (all sections)"]
version: "{{ metadata.version }}"
language: "en"
generated_at: "{{ metadata.generated_at }}"
---

# Statement of Applicability (SoA)
*{{ company.name }} - {{ system.name }}*

> Lists all necessary controls and the justification for inclusion/exclusion.  
> Generated: {{ metadata.generated_at }}

| Control_ID | Control_Name | Applicability | Justification | Evidence_Document | Owner | Status | Due_Date | Remarks | AI_Act_Reference |
|------------|--------------|:-------------:|---------------|-------------------|-------|--------|----------:|---------|------------------|
{% if controls %}
{% for control in controls %}
| {{ control.iso_clause }} | {{ control.name }} | Yes | {{ control.rationale }} | {% if control.evidence %}{% for ev in control.evidence %}{{ ev.label }}{% if not loop.last %}; {% endif %}{% endfor %}{% else %}No evidence{% endif %} | {{ control.owner_email }} | {{ control.status }} | {% if control.due_date %}{{ control.due_date }}{% else %}Not set{% endif %} | {{ control.priority }} | Annex IV |
{% endfor %}

## Evidence Citations
{% for control in controls %}
{% if control.evidence %}
**{{ control.iso_clause }} - {{ control.name }}:**
{% for ev in control.evidence %}
- [EV-{{ ev.id }} | {{ ev.label }} | sha256:{{ ev.checksum[:16] if ev.checksum else 'N/A' }}]
{% endfor %}
{% endif %}
{% endfor %}
{% else %}
| A.5.1 | Leadership & commitment | Yes | Governance objectives approved | No evidence | {{ system.owner_email }} | Missing | Not set | High | Annex IV §2 |
| A.6.1 | Risk management | Yes | Process aligned with ISO 31000 | No evidence | {{ system.owner_email }} | Missing | Not set | High | Annex IV §6 |
| A.6.2 | AI life‑cycle controls | Yes | Design/Dev/Deploy procedures | No evidence | {{ system.owner_email }} | Missing | Not set | High | Annex IV §8 |
| A.7.x | Data management | Yes | Data governance in place | No evidence | {{ system.owner_email }} | Missing | Not set | High | Annex IV §8.4 |
| A.8.x | Transparency & reporting | Yes | User/system info available | No evidence | {{ system.owner_email }} | Missing | Not set | High | Annex IV §2 |
| A.9.1 | Monitoring & measurement | Yes | Logging + PMM | No evidence | {{ system.owner_email }} | Missing | Not set | High | Art. 72 |
{% endif %}

> {% if controls %}Total controls: {{ controls|length }}{% else %}No controls have been defined yet. Please complete the controls assessment in the system configuration.{% endif %}
