---
template_id: model_card_v1
iso_clauses: ["A.6.2","B.6"]
ai_act: ["Annex IV §8"]
version: "1.0.0"
language: "en"
generated_at: "2025-10-22T11:54:53.512307+00:00"
---

# Model Card — Credit Scoring AI

**Organization:** Demo Organization  
**System:** Credit Scoring AI  
**Domain:** Finance  
**AI Act Classification:** high  
**Generated:** 2025-10-22T11:54:53.512307+00:00

## Overview
- **Objective:** Automated loan eligibility scoring (approve/deny up to €25k)
- **Algorithm:** AI/ML System
- **Owner:** ana@techcorp.ai
- **Lifecycle Stage:** Development
- **Deployment Context:** Public-facing application
- **General Purpose AI:** No
- **Biometric Data:** No
- **Personal Data:** Yes

## Data & Training


**Data Sources:**  
Experian credit bureau; internal loan history


**Quality Assurance:** Data quality checks are performed as part of the PMM process  
**Bias Testing:** Fairness metrics monitored: Accuracy, precision, recall

## Performance


*Model versioning not yet configured*


**Performance Monitoring:**  
- Drift threshold: 10%  
- Retention period: 12 months  
- Review frequency: quarterly

## Explainability & Limitations

**Transparency:** Explanations provided to users  
**Known Limitations:** applicants (adults)



## Human Oversight & Change Management


**Oversight Mode:** in_the_loop  
**Review Trigger:**   
**Override Rights:** Not configured  
**Intervention Rules:** Standard intervention procedures


**Version Control:** Not yet implemented  
**Rollback Policy:** Rollback to previous version if performance degrades beyond thresholds



---

**References:** ISO 42001 A.6.2/B.6; AI Act Annex IV §8.