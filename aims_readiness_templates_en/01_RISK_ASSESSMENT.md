---
template_id: risk_assessment_v1
iso_clauses: ["6.1","Annex C"]
ai_act: ["Annex IV §6"]
version: "{{ metadata.version }}"
language: "en"
generated_at: "{{ metadata.generated_at }}"
---

# Risk Management Plan — {{ system.name }}
*Based on ISO/IEC 42001 clause 6.1 and Annex C.*

**Organization:** {{ company.name }}  
**System:** {{ system.name }}  
**Domain:** {{ system.domain }}  
**AI Act Classification:** {{ system.ai_act_class }}  
**Generated:** {{ metadata.generated_at }}

## 1. Purpose  
Identify, analyse, evaluate and treat risks related to AI systems operated by {{ company.name }}.

## 2. Scope  
All AI systems operated by {{ company.name }}, including the {{ system.name }} system, pilots and third‑party models.

## 3. Methodology  
- ISO 31000 principles (Identify → Analyse → Evaluate → Treat → Monitor).  
- Risk register maintained in this document; update after incidents or significant model changes.  

## 4. Roles and Responsibilities  
| Role | Responsibility |
|------|----------------|
| AI Governance Lead | Maintains the risk register; reports to top management. |
| System Owner | Identifies operational risks; owns mitigation actions. |
| Compliance Officer | Aligns risks with legal/ethical requirements. |

## 5. Risk Register
{% if risks %}
| ID | Risk | Likelihood | Impact | Level | Mitigation | Owner | Status |
|----|------|-----------:|-------:|:-----:|------------|--------|--------|
{% for risk in risks %}
| R-{{ "%03d"|format(loop.index) }} | {{ risk.description }} | {{ risk.likelihood }} | {{ risk.impact }} | {{ risk.residual_risk }} | {{ risk.mitigation }} | {{ risk.owner_email }} | {{ risk.priority }} |
{% endfor %}
{% else %}
*No risks have been identified for this system yet. Please complete the risk assessment in the system configuration.*
{% endif %}

## 6. Monitoring & Review  
Quarterly review or after incidents; metrics: open risks, MTTR, residual risk trend.

## 7. References  
ISO/IEC 42001 §6.1; ISO/IEC 23894; EU AI Act Annex IV §6.
