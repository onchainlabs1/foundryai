"""
Document Context Service

Composes all wizard data for document generation with no placeholders.
This service queries all relevant tables and returns structured context
for Jinja2 templates to use real data instead of boilerplate.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import (
    Organization, AISystem, AIRisk, Control, Oversight, PMM, 
    Evidence, FRIA, OnboardingData, ModelVersion, DocumentApproval
)


class DocumentContextService:
    """Service to build complete document context from all wizard data."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def build_system_context(self, system_id: int, org_id: int, doc_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Build complete context for a system including:
        - Company/org data
        - System data  
        - Risk data
        - Controls
        - Oversight
        - PMM
        - Evidence links
        - FRIA (if exists)
        """
        
        # Get organization data
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise ValueError(f"Organization {org_id} not found")
        
        # Get system data
        system = self.db.query(AISystem).filter(
            and_(AISystem.id == system_id, AISystem.org_id == org_id)
        ).first()
        if not system:
            raise ValueError(f"System {system_id} not found for org {org_id}")
        
        # Get risks
        risks = self.db.query(AIRisk).filter(
            and_(AIRisk.system_id == system_id, AIRisk.org_id == org_id)
        ).all()
        
        # Get controls
        controls = self.db.query(Control).filter(
            and_(Control.system_id == system_id, Control.org_id == org_id)
        ).order_by(Control.iso_clause).all()
        
        # Get oversight
        oversight = self.db.query(Oversight).filter(
            and_(Oversight.system_id == system_id, Oversight.org_id == org_id)
        ).first()
        
        # Get PMM
        pmm = self.db.query(PMM).filter(
            and_(PMM.system_id == system_id, PMM.org_id == org_id)
        ).first()
        
        # Get evidence
        evidence = self.db.query(Evidence).filter(
            and_(Evidence.system_id == system_id, Evidence.org_id == org_id)
        ).all()
        
        # Get FRIA (latest)
        fria = self.db.query(FRIA).filter(
            and_(FRIA.system_id == system_id, FRIA.org_id == org_id)
        ).order_by(FRIA.created_at.desc()).first()
        
        # Get onboarding data
        onboarding_data = self.db.query(OnboardingData).filter(
            and_(OnboardingData.system_id == system_id, OnboardingData.org_id == org_id)
        ).first()
        
        # Get model versions
        model_versions = self.db.query(ModelVersion).filter(
            and_(ModelVersion.system_id == system_id, ModelVersion.org_id == org_id)
        ).order_by(ModelVersion.released_at.desc()).all()
        
        # Get latest version
        latest_version = model_versions[0] if model_versions else None
        
        # Get approval for specific document type (if provided)
        approval = None
        if doc_type:
            approval = self.db.query(DocumentApproval).filter(
                and_(
                    DocumentApproval.system_id == system_id,
                    DocumentApproval.org_id == org_id,
                    DocumentApproval.doc_type == doc_type
                )
            ).first()
        
        # Build context with defaults for missing data
        context = {
            # Company/Organization
            "company": {
                "name": org.name or "Unknown Organization",
                "primary_contact_name": org.primary_contact_name or "Contact Person",
                "primary_contact_email": org.primary_contact_email or "contact@company.com",
                "dpo_contact_name": org.dpo_contact_name or "DPO",
                "dpo_contact_email": org.dpo_contact_email or "dpo@company.com",
                "org_role": org.org_role or "deployer"
            },
            
            # System
            "system": {
                "id": system.id,
                "name": system.name or "Unnamed System",
                "purpose": system.purpose or "System purpose not defined",
                "domain": system.domain or "General",
                "owner_email": system.owner_email or "owner@company.com",
                "deployment_context": system.deployment_context or "Internal",
                "lifecycle_stage": system.lifecycle_stage or "Development",
                "affected_users": system.affected_users or "Internal users",
                "third_party_providers": system.third_party_providers or "None",
                "risk_category": system.risk_category or "Medium",
                "ai_act_class": system.ai_act_class or "minimal",
                "uses_biometrics": system.uses_biometrics or False,
                "is_general_purpose_ai": system.is_general_purpose_ai or False,
                "impacts_fundamental_rights": system.impacts_fundamental_rights or False,
                "personal_data_processed": system.personal_data_processed or False,
                "uses_gpai": system.uses_gpai or False,
                "biometrics_in_public": system.biometrics_in_public or False,
                "annex3_categories": system.annex3_categories or "[]",
                "impacted_groups": system.impacted_groups or "Internal users",
                "requires_fria": self._compute_requires_fria(system)
            },
            
            # Risks
            "risks": [
                {
                    "id": risk.id,
                    "description": risk.description or "Risk not described",
                    "likelihood": risk.likelihood or "M",
                    "impact": risk.impact or "M", 
                    "mitigation": risk.mitigation or "Mitigation not defined",
                    "residual_risk": risk.residual_risk or "Medium",
                    "owner_email": risk.owner_email or "owner@company.com",
                    "priority": risk.priority or "medium",
                    "due_date": risk.due_date.isoformat() if risk.due_date else None
                }
                for risk in risks
            ],
            
            # Controls
            "controls": [
                {
                    "id": control.id,
                    "iso_clause": control.iso_clause or "A.1.1",
                    "name": control.name or "Control not named",
                    "priority": control.priority or "medium",
                    "status": control.status or "missing",
                    "owner_email": control.owner_email or "owner@company.com",
                    "due_date": control.due_date.isoformat() if control.due_date else None,
                    "rationale": control.rationale or "Rationale not provided",
                    "evidence": [
                        {
                            "id": ev.id,
                            "label": ev.label or "Evidence",
                            "file_path": ev.file_path or "",
                            "checksum": ev.checksum or "",
                            "version": ev.version or "1.0"
                        }
                        for ev in evidence if ev.control_id == control.id
                    ]
                }
                for control in controls
            ],
            
            # Oversight
            "oversight": {
                "mode": oversight.oversight_mode if oversight else "in_the_loop",
                "intervention_rules": oversight.intervention_rules if oversight else "Standard intervention procedures",
                "manual_override": oversight.manual_override if oversight else True,
                "appeals_channel": oversight.appeals_channel if oversight else "support@company.com",
                "appeals_sla_days": oversight.appeals_sla_days if oversight else 5,
                "appeals_responsible_email": oversight.appeals_responsible_email if oversight else "support@company.com",
                "ethics_committee": oversight.ethics_committee if oversight else False,
                "training_plan": oversight.training_plan if oversight else "Standard training procedures",
                "comm_plan": oversight.comm_plan if oversight else "Standard communication procedures",
                "external_disclosure": oversight.external_disclosure if oversight else False
            } if oversight else {
                "mode": "in_the_loop",
                "intervention_rules": "Standard intervention procedures",
                "manual_override": True,
                "appeals_channel": "support@company.com",
                "appeals_sla_days": 5,
                "appeals_responsible_email": "support@company.com",
                "ethics_committee": False,
                "training_plan": "Standard training procedures",
                "comm_plan": "Standard communication procedures",
                "external_disclosure": False
            },
            
            # PMM
            "pmm": {
                "logging_scope": pmm.logging_scope if pmm else "System inputs, outputs, and decisions",
                "retention_months": pmm.retention_months if pmm else 12,
                "drift_threshold": pmm.drift_threshold if pmm else "10%",
                "fairness_metrics": pmm.fairness_metrics if pmm else "Accuracy, precision, recall",
                "incident_tool": pmm.incident_tool if pmm else "Internal ticketing system",
                "audit_frequency": pmm.audit_frequency if pmm else "quarterly",
                "management_review_frequency": pmm.management_review_frequency if pmm else "quarterly",
                "improvement_plan": pmm.improvement_plan if pmm else "Continuous improvement based on monitoring results",
                "eu_db_required": pmm.eu_db_required if pmm else False,
                "eu_db_status": pmm.eu_db_status if pmm else "pending"
            } if pmm else {
                "logging_scope": "System inputs, outputs, and decisions",
                "retention_months": 12,
                "drift_threshold": "10%",
                "fairness_metrics": "Accuracy, precision, recall",
                "incident_tool": "Internal ticketing system",
                "audit_frequency": "quarterly",
                "management_review_frequency": "quarterly",
                "improvement_plan": "Continuous improvement based on monitoring results",
                "eu_db_required": False,
                "eu_db_status": "pending"
            },
            
            # Evidence
            "evidence": [
                {
                    "id": ev.id,
                    "label": ev.label or "Evidence",
                    "file_path": ev.file_path or "",
                    "checksum": ev.checksum or "",
                    "version": ev.version or "1.0",
                    "control_id": ev.control_id,
                    "iso_clause": ev.iso42001_clause or "A.1.1"
                }
                for ev in evidence
            ],
            
            # FRIA
            "fria": {
                "id": fria.id,
                "applicable": fria.applicable,
                "status": fria.status,
                "answers": fria.answers_json,
                "summary": fria.summary_md,
                "created_at": fria.created_at.isoformat() if fria.created_at else None
            } if fria else None,
            
            # Model Version
            "model_version": {
                "version": latest_version.version,
                "released_at": latest_version.released_at.isoformat() if latest_version.released_at else None,
                "approver_email": latest_version.approver_email,
                "notes": latest_version.notes,
                "artifact_hash": latest_version.artifact_hash
            } if latest_version else None,
            
            # All versions
            "model_versions": [
                {
                    "version": v.version,
                    "released_at": v.released_at.isoformat() if v.released_at else None,
                    "approver_email": v.approver_email,
                    "notes": v.notes,
                    "artifact_hash": v.artifact_hash
                }
                for v in model_versions
            ],
            
            # Document Approval (for specific doc_type)
            "approval": {
                "status": approval.status,
                "submitted_by": approval.submitted_by,
                "submitted_at": approval.submitted_at.isoformat() if approval.submitted_at else None,
                "approver_email": approval.approver_email,
                "approved_at": approval.approved_at.isoformat() if approval.approved_at else None,
                "document_hash": approval.document_hash,
                "notes": approval.notes
            } if approval else None,
            
            # Metadata
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "version": "1.0.0",
                "system_id": system_id,
                "org_id": org_id,
                "has_risks": len(risks) > 0,
                "has_controls": len(controls) > 0,
                "has_evidence": len(evidence) > 0,
                "has_fria": fria is not None,
                "risk_count": len(risks),
                "control_count": len(controls),
                "evidence_count": len(evidence)
            }
        }
        
        return context
    
    def _compute_requires_fria(self, system: AISystem) -> bool:
        """Compute if system requires FRIA based on EU AI Act criteria."""
        return (
            system.impacts_fundamental_rights or
            system.uses_biometrics or
            system.biometrics_in_public or
            system.ai_act_class == 'high-risk'
        )
    
    def get_annex3_categories(self, system: AISystem) -> List[str]:
        """Get Annex III categories for high-risk systems."""
        if system.ai_act_class != 'high-risk':
            return []
        
        # Parse annex3_categories JSON or return defaults
        try:
            import json
            if system.annex3_categories:
                return json.loads(system.annex3_categories)
        except:
            pass
        
        # Default categories based on system characteristics
        categories = []
        if system.uses_biometrics:
            categories.append("Biometric identification and categorization")
        if system.domain in ["Education", "Employment"]:
            categories.append("Education and vocational training")
        if system.domain in ["Employment", "Worker management"]:
            categories.append("Employment, worker management")
        
        return categories
    
    def get_evidence_citations(self, evidence_list: List[Evidence]) -> Dict[int, str]:
        """Generate citation format for evidence."""
        citations = {}
        for ev in evidence_list:
            if ev.checksum:
                citations[ev.id] = f"[EV-{ev.id} | {ev.label} | sha256:{ev.checksum[:16]}]"
            else:
                citations[ev.id] = f"[EV-{ev.id} | {ev.label}]"
        return citations
