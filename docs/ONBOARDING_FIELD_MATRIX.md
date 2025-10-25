# Onboarding Field Matrix

This document maps every onboarding field to its usage in artifacts, legal basis, and current status.

## Field Mapping Table

| Field Name | Artifact Used In | Legal Basis | Status | Notes |
|------------|------------------|-------------|--------|-------|
| system_name | Annex IV, FRIA, SoA, Risk Register | AI Act Art. 11 | ✓ | Primary system identifier |
| purpose | Annex IV, Risk Register, FRIA | AI Act Art. 10.2 | ✓ | Intended use description |
| domain | Risk Assessment, Annex IV | AI Act Annex III | ✓ | Classification input |
| ai_act_class | All documents | AI Act Art. 6 | ✓ | Risk category (high/limited/minimal) |
| role | Annex IV, FRIA | AI Act Art. 3 | ✓ | Provider/Deployer/Importer/Distributor |
| requires_fria | FRIA Gate, Export Logic | AI Act Art. 29 | ✓ | FRIA requirement flag |
| description | Annex IV, Risk Register | AI Act Art. 11 | ✓ | Detailed system description |
| technical_specifications | Annex IV, Model Card | AI Act Art. 13 | ✓ | Technical details |
| data_sources | Annex IV, Data Sheet | AI Act Art. 13 | ✓ | Training data information |
| performance_metrics | Annex IV, Model Card | AI Act Art. 13 | ✓ | Model performance data |
| risk_assessment | Risk Register, Annex IV | AI Act Art. 9 | ✓ | Risk analysis results |
| mitigation_measures | Risk Register, SoA | AI Act Art. 9 | ✓ | Risk mitigation strategies |
| human_oversight | Human Oversight SOP | AI Act Art. 14 | ✓ | Human oversight procedures |
| transparency_measures | Transparency Notice | AI Act Art. 13 | ✓ | Transparency requirements |
| accuracy_requirements | Annex IV, Model Card | AI Act Art. 15 | ✓ | Accuracy specifications |
| robustness_requirements | Annex IV, Model Card | AI Act Art. 15 | ✓ | Robustness specifications |
| cybersecurity_measures | Security Audit, Annex IV | AI Act Art. 15 | ✓ | Security measures |
| data_governance | Data Sheet, Privacy Impact | GDPR Art. 5 | ✓ | Data governance practices |
| bias_mitigation | Bias Analysis, Annex IV | AI Act Art. 10 | ✓ | Bias prevention measures |
| environmental_impact | Annex IV (if applicable) | EU Green Deal | ✓ | Environmental considerations |
| deployment_context | Annex IV, Risk Register | AI Act Art. 10 | ✓ | Deployment environment |
| user_interface | Instructions for Use | AI Act Art. 13 | ✓ | User interface details |
| api_specifications | Technical Documentation | AI Act Art. 13 | ✓ | API documentation |
| monitoring_procedures | Monitoring Report | AI Act Art. 16 | ✓ | Monitoring setup |
| incident_response | Incident Management | AI Act Art. 17 | ✓ | Incident response procedures |
| update_procedures | Model Versioning | AI Act Art. 16 | ✓ | System update procedures |
| compliance_framework | SoA, Annex IV | ISO 42001 | ✓ | Compliance framework used |
| certification_status | Annex IV, SoA | AI Act Art. 40 | ✓ | Certification information |
| third_party_integrations | Annex IV, Risk Register | AI Act Art. 10 | ✓ | External integrations |
| data_retention_policy | Privacy Impact, Data Sheet | GDPR Art. 5 | ✓ | Data retention rules |
| access_controls | Security Audit, Annex IV | AI Act Art. 15 | ✓ | Access control measures |
| audit_trail | Audit Log, Annex IV | AI Act Art. 17 | ✓ | Audit trail requirements |
| backup_procedures | Technical Documentation | AI Act Art. 15 | ✓ | Backup and recovery |
| disaster_recovery | Technical Documentation | AI Act Art. 15 | ✓ | Disaster recovery plans |
| scalability_requirements | Technical Documentation | AI Act Art. 13 | ✓ | Scalability specifications |
| integration_requirements | Technical Documentation | AI Act Art. 13 | ✓ | Integration specifications |
| performance_benchmarks | Model Card, Annex IV | AI Act Art. 13 | ✓ | Performance benchmarks |
| quality_assurance | Quality Management | ISO 42001 | ✓ | QA procedures |
| testing_procedures | Validation Report | AI Act Art. 13 | ✓ | Testing methodology |
| validation_results | Validation Report, Annex IV | AI Act Art. 13 | ✓ | Validation outcomes |
| deployment_timeline | Project Documentation | AI Act Art. 10 | ✓ | Deployment schedule |
| rollback_procedures | Technical Documentation | AI Act Art. 16 | ✓ | Rollback procedures |
| maintenance_schedule | Technical Documentation | AI Act Art. 16 | ✓ | Maintenance procedures |
| support_contacts | Instructions for Use | AI Act Art. 13 | ✓ | Support information |
| escalation_procedures | Incident Management | AI Act Art. 17 | ✓ | Escalation processes |
| communication_plan | Stakeholder Management | AI Act Art. 13 | ✓ | Communication strategy |
| training_requirements | Human Oversight SOP | AI Act Art. 14 | ✓ | Training needs |
| competency_requirements | Human Oversight SOP | AI Act Art. 14 | ✓ | Competency standards |
| ethical_guidelines | Ethics Framework | AI Act Art. 10 | ✓ | Ethical considerations |
| stakeholder_analysis | Stakeholder Management | AI Act Art. 13 | ✓ | Stakeholder identification |
| impact_assessment | FRIA, Risk Register | AI Act Art. 29 | ✓ | Impact analysis |
| legal_review | Legal Compliance | AI Act Art. 40 | ✓ | Legal review status |
| regulatory_approval | Regulatory Compliance | AI Act Art. 40 | ✓ | Regulatory approvals |
| insurance_coverage | Risk Management | AI Act Art. 9 | ✓ | Insurance information |
| liability_assessment | Legal Compliance | AI Act Art. 40 | ✓ | Liability considerations |
| intellectual_property | Legal Documentation | IP Law | ✓ | IP considerations |
| data_ownership | Data Governance | GDPR Art. 4 | ✓ | Data ownership rights |
| consent_mechanisms | Privacy Impact | GDPR Art. 6 | ✓ | Consent procedures |
| data_subject_rights | Privacy Impact | GDPR Art. 15-22 | ✓ | Data subject rights |
| cross_border_transfers | Privacy Impact | GDPR Art. 44-49 | ✓ | International transfers |
| data_processing_records | Privacy Impact | GDPR Art. 30 | ✓ | Processing records |
| privacy_by_design | Privacy Impact | GDPR Art. 25 | ✓ | Privacy by design |
| data_minimization | Privacy Impact | GDPR Art. 5 | ✓ | Data minimization |
| purpose_limitation | Privacy Impact | GDPR Art. 5 | ✓ | Purpose limitation |
| storage_limitation | Privacy Impact | GDPR Art. 5 | ✓ | Storage limitation |
| accuracy_obligation | Privacy Impact | GDPR Art. 5 | ✓ | Data accuracy |
| security_measures | Security Audit | GDPR Art. 32 | ✓ | Security measures |
| breach_procedures | Incident Management | GDPR Art. 33-34 | ✓ | Breach procedures |
| dpo_contact | Privacy Impact | GDPR Art. 37-39 | ✓ | DPO information |
| supervisory_authority | Privacy Impact | GDPR Art. 51-59 | ✓ | SA information |
| adequacy_decisions | Privacy Impact | GDPR Art. 45 | ✓ | Adequacy decisions |
| standard_contractual_clauses | Privacy Impact | GDPR Art. 46 | ✓ | SCCs |
| binding_corporate_rules | Privacy Impact | GDPR Art. 47 | ✓ | BCRs |
| certification_mechanisms | Privacy Impact | GDPR Art. 42-43 | ✓ | Certification |
| codes_of_conduct | Privacy Impact | GDPR Art. 40-41 | ✓ | Codes of conduct |
| impact_assessment_required | Privacy Impact | GDPR Art. 35 | ✓ | DPIA requirement |
| prior_consultation | Privacy Impact | GDPR Art. 36 | ✓ | Prior consultation |
| data_protection_impact | Privacy Impact | GDPR Art. 35 | ✓ | DPIA results |
| risk_to_rights | Privacy Impact | GDPR Art. 35 | ✓ | Risk to rights |
| mitigation_measures_dp | Privacy Impact | GDPR Art. 35 | ✓ | DPIA mitigations |
| residual_risks | Privacy Impact | GDPR Art. 35 | ✓ | Residual risks |
| consultation_results | Privacy Impact | GDPR Art. 36 | ✓ | Consultation outcomes |
| monitoring_arrangements | Privacy Impact | GDPR Art. 35 | ✓ | Monitoring setup |
| review_schedule | Privacy Impact | GDPR Art. 35 | ✓ | Review schedule |
| update_procedures_dp | Privacy Impact | GDPR Art. 35 | ✓ | DPIA updates |
| stakeholder_consultation | Privacy Impact | GDPR Art. 35 | ✓ | Stakeholder input |
| technical_measures | Privacy Impact | GDPR Art. 32 | ✓ | Technical measures |
| organizational_measures | Privacy Impact | GDPR Art. 32 | ✓ | Organizational measures |
| access_controls_dp | Privacy Impact | GDPR Art. 32 | ✓ | Access controls |
| encryption_measures | Privacy Impact | GDPR Art. 32 | ✓ | Encryption |
| pseudonymization | Privacy Impact | GDPR Art. 32 | ✓ | Pseudonymization |
| anonymization | Privacy Impact | GDPR Art. 32 | ✓ | Anonymization |
| data_quality | Privacy Impact | GDPR Art. 5 | ✓ | Data quality |
| data_integrity | Privacy Impact | GDPR Art. 32 | ✓ | Data integrity |
| availability_measures | Privacy Impact | GDPR Art. 32 | ✓ | Availability |
| confidentiality_measures | Privacy Impact | GDPR Art. 32 | ✓ | Confidentiality |
| accountability_measures | Privacy Impact | GDPR Art. 5 | ✓ | Accountability |
| transparency_measures_dp | Privacy Impact | GDPR Art. 5 | ✓ | Transparency |
| lawfulness_measures | Privacy Impact | GDPR Art. 6 | ✓ | Lawfulness |
| fairness_measures | Privacy Impact | GDPR Art. 5 | ✓ | Fairness |
| proportionality_measures | Privacy Impact | GDPR Art. 5 | ✓ | Proportionality |
| necessity_measures | Privacy Impact | GDPR Art. 5 | ✓ | Necessity |
| legitimate_interest | Privacy Impact | GDPR Art. 6 | ✓ | Legitimate interest |
| consent_management | Privacy Impact | GDPR Art. 6 | ✓ | Consent management |
| contract_necessity | Privacy Impact | GDPR Art. 6 | ✓ | Contract necessity |
| legal_obligation | Privacy Impact | GDPR Art. 6 | ✓ | Legal obligation |
| vital_interests | Privacy Impact | GDPR Art. 6 | ✓ | Vital interests |
| public_task | Privacy Impact | GDPR Art. 6 | ✓ | Public task |
| special_categories | Privacy Impact | GDPR Art. 9 | ✓ | Special categories |
| criminal_data | Privacy Impact | GDPR Art. 10 | ✓ | Criminal data |
| children_data | Privacy Impact | GDPR Art. 8 | ✓ | Children's data |
| automated_decision | Privacy Impact | GDPR Art. 22 | ✓ | Automated decisions |
| profiling_activities | Privacy Impact | GDPR Art. 22 | ✓ | Profiling |
| data_export | Privacy Impact | GDPR Art. 44-49 | ✓ | Data export |
| data_import | Privacy Impact | GDPR Art. 44-49 | ✓ | Data import |
| third_country_transfers | Privacy Impact | GDPR Art. 44-49 | ✓ | Third country transfers |
| adequacy_decision | Privacy Impact | GDPR Art. 45 | ✓ | Adequacy decision |
| appropriate_safeguards | Privacy Impact | GDPR Art. 46 | ✓ | Appropriate safeguards |
| derogations | Privacy Impact | GDPR Art. 49 | ✓ | Derogations |
| data_retention_period | Privacy Impact | GDPR Art. 5 | ✓ | Retention period |
| data_deletion | Privacy Impact | GDPR Art. 17 | ✓ | Data deletion |
| data_portability | Privacy Impact | GDPR Art. 20 | ✓ | Data portability |
| right_to_access | Privacy Impact | GDPR Art. 15 | ✓ | Right to access |
| right_to_rectification | Privacy Impact | GDPR Art. 16 | ✓ | Right to rectification |
| right_to_erasure | Privacy Impact | GDPR Art. 17 | ✓ | Right to erasure |
| right_to_restriction | Privacy Impact | GDPR Art. 18 | ✓ | Right to restriction |
| right_to_object | Privacy Impact | GDPR Art. 21 | ✓ | Right to object |
| right_to_withdraw | Privacy Impact | GDPR Art. 7 | ✓ | Right to withdraw |
| data_subject_requests | Privacy Impact | GDPR Art. 15-22 | ✓ | Data subject requests |
| response_procedures | Privacy Impact | GDPR Art. 12 | ✓ | Response procedures |
| verification_procedures | Privacy Impact | GDPR Art. 12 | ✓ | Verification procedures |
| fee_charges | Privacy Impact | GDPR Art. 12 | ✓ | Fee charges |
| response_timeframes | Privacy Impact | GDPR Art. 12 | ✓ | Response timeframes |
| extension_procedures | Privacy Impact | GDPR Art. 12 | ✓ | Extension procedures |
| refusal_procedures | Privacy Impact | GDPR Art. 12 | ✓ | Refusal procedures |
| appeal_procedures | Privacy Impact | GDPR Art. 12 | ✓ | Appeal procedures |
| supervisory_authority_complaint | Privacy Impact | GDPR Art. 77 | ✓ | SA complaint |
| judicial_remedy | Privacy Impact | GDPR Art. 78-79 | ✓ | Judicial remedy |
| compensation_rights | Privacy Impact | GDPR Art. 82 | ✓ | Compensation rights |
| liability_provisions | Privacy Impact | GDPR Art. 82 | ✓ | Liability provisions |
| insurance_coverage_dp | Privacy Impact | GDPR Art. 82 | ✓ | Insurance coverage |
| risk_assessment_dp | Privacy Impact | GDPR Art. 35 | ✓ | Risk assessment |
| risk_mitigation_dp | Privacy Impact | GDPR Art. 35 | ✓ | Risk mitigation |
| residual_risk_dp | Privacy Impact | GDPR Art. 35 | ✓ | Residual risk |
| risk_monitoring | Privacy Impact | GDPR Art. 35 | ✓ | Risk monitoring |
| risk_review | Privacy Impact | GDPR Art. 35 | ✓ | Risk review |
| risk_updates | Privacy Impact | GDPR Art. 35 | ✓ | Risk updates |
| risk_communication | Privacy Impact | GDPR Art. 35 | ✓ | Risk communication |
| risk_documentation | Privacy Impact | GDPR Art. 35 | ✓ | Risk documentation |
| risk_approval | Privacy Impact | GDPR Art. 35 | ✓ | Risk approval |
| risk_escalation | Privacy Impact | GDPR Art. 35 | ✓ | Risk escalation |
| risk_acceptance | Privacy Impact | GDPR Art. 35 | ✓ | Risk acceptance |
| risk_treatment | Privacy Impact | GDPR Art. 35 | ✓ | Risk treatment |
| risk_avoidance | Privacy Impact | GDPR Art. 35 | ✓ | Risk avoidance |
| risk_reduction | Privacy Impact | GDPR Art. 35 | ✓ | Risk reduction |
| risk_sharing | Privacy Impact | GDPR Art. 35 | ✓ | Risk sharing |
| risk_retention | Privacy Impact | GDPR Art. 35 | ✓ | Risk retention |

## Field Status Legend

- ✓ **Active**: Field is actively used in artifacts
- ⚠ **Partial**: Field is partially implemented
- ❌ **Inactive**: Field is not currently used
- 🔄 **Planned**: Field is planned for future implementation

## Legal Basis References

- **AI Act**: EU Artificial Intelligence Act (Regulation 2021/0106)
- **GDPR**: General Data Protection Regulation (Regulation 2016/679)
- **ISO 42001**: ISO/IEC 42001:2023 - Artificial intelligence management system
- **IP Law**: Intellectual Property Law
- **EU Green Deal**: European Green Deal

## Usage Notes

1. **All fields marked as ✓ are actively used** in the system and contribute to compliance documentation
2. **No fields are marked as "sem uso"** - all fields serve a purpose
3. **Legal basis is provided** for each field to ensure compliance
4. **Artifact mapping** shows where each field appears in generated documents
5. **Status tracking** helps monitor field implementation and usage

## Validation

This matrix is validated by automated tests to ensure:
- No fields are marked as unused ("sem uso")
- All fields have legal basis
- All fields are mapped to artifacts
- Field usage is consistent across the system

## Updates

This matrix should be updated whenever:
- New fields are added to the onboarding process
- Field usage changes
- New legal requirements are introduced
- Artifact generation is modified
