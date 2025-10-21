"""
Blocking Issues Service

Checks system completeness and identifies blocking issues that prevent
audit-grade document generation. Returns structured issues with severity,
title, description, and action items.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import AISystem, Control, FRIA, PMM, AIRisk, Evidence


class BlockingIssuesService:
    """Service to identify blocking issues for audit-grade compliance."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_blocking_issues(self, system_id: int, org_id: int) -> List[Dict[str, Any]]:
        """
        Get all blocking issues for a system.
        
        Returns:
            List of blocking issues with severity, title, description, action
        """
        issues = []
        
        # Get system
        system = (
            self.db.query(AISystem)
            .filter(and_(AISystem.id == system_id, AISystem.org_id == org_id))
            .first()
        )
        if not system:
            return [{
                "id": "system_not_found",
                "severity": "critical",
                "title": "System not found",
                "description": "The specified system does not exist or you don't have access to it.",
                "action": "Contact administrator",
                "action_url": None
            }]
        
        # Check FRIA requirements
        if system.requires_fria_computed:
            fria = (
                self.db.query(FRIA)
                .filter(and_(FRIA.system_id == system_id, FRIA.org_id == org_id))
                .order_by(FRIA.created_at.desc())
                .first()
            )
            if not fria:
                issues.append({
                    "id": "fria_required_missing",
                    "severity": "critical",
                    "title": "FRIA assessment required",
                    "description": "High-risk system requires FRIA assessment (Article 27 EU AI Act)",
                    "action": "Complete FRIA assessment",
                    "action_url": f"/systems/{system_id}/fria"
                })
            elif fria.status != 'submitted':
                issues.append({
                    "id": "fria_incomplete",
                    "severity": "critical", 
                    "title": "FRIA assessment incomplete",
                    "description": f"FRIA assessment exists but status is '{fria.status}' (must be 'submitted')",
                    "action": "Complete FRIA assessment",
                    "action_url": f"/systems/{system_id}/fria"
                })
        
        # Check controls completeness
        controls = (
            self.db.query(Control)
            .filter(and_(Control.system_id == system_id, Control.org_id == org_id))
            .all()
        )
        
        if not controls:
            issues.append({
                "id": "no_controls_defined",
                "severity": "high",
                "title": "No controls defined",
                "description": "No ISO 42001 controls have been defined for this system",
                "action": "Define controls",
                "action_url": f"/systems/{system_id}/controls"
            })
        else:
            # Check for controls missing owners
            controls_missing_owner = [
                c for c in controls if not c.owner_email
            ]
            if controls_missing_owner:
                issues.append({
                    "id": "control_missing_owner",
                    "severity": "high",
                    "title": f"{len(controls_missing_owner)} controls missing owners",
                    "description": f"Controls {', '.join([c.iso_clause for c in controls_missing_owner[:3]])}{'...' if len(controls_missing_owner) > 3 else ''} need assigned owners",
                    "action": "Assign control owners",
                    "action_url": f"/systems/{system_id}/controls"
                })
            
            # Check for controls with missing status
            controls_missing_status = [
                c for c in controls if c.status == 'missing'
            ]
            if controls_missing_status:
                issues.append({
                    "id": "control_status_missing",
                    "severity": "medium",
                    "title": f"{len(controls_missing_status)} controls not implemented",
                    "description": f"Controls {', '.join([c.iso_clause for c in controls_missing_status[:3]])}{'...' if len(controls_missing_status) > 3 else ''} are marked as missing",
                    "action": "Update control status",
                    "action_url": f"/systems/{system_id}/controls"
                })
        
        # Check PMM completeness
        pmm = (
            self.db.query(PMM)
            .filter(and_(PMM.system_id == system_id, PMM.org_id == org_id))
            .first()
        )
        
        if not pmm:
            issues.append({
                "id": "pmm_missing",
                "severity": "high",
                "title": "Post-Market Monitoring not configured",
                "description": "PMM configuration is required for audit-grade compliance",
                "action": "Configure PMM",
                "action_url": f"/systems/{system_id}/pmm"
            })
        else:
            if not pmm.retention_months:
                issues.append({
                    "id": "pmm_missing_retention",
                    "severity": "medium",
                    "title": "PMM retention period not set",
                    "description": "Data retention period must be specified for PMM",
                    "action": "Set retention period",
                    "action_url": f"/systems/{system_id}/pmm"
                })
            
            if not pmm.logging_scope:
                issues.append({
                    "id": "pmm_missing_logging_scope",
                    "severity": "medium",
                    "title": "PMM logging scope not defined",
                    "description": "Logging scope must be specified for PMM",
                    "action": "Define logging scope",
                    "action_url": f"/systems/{system_id}/pmm"
                })
        
        # Check risk coverage
        risks = (
            self.db.query(AIRisk)
            .filter(and_(AIRisk.system_id == system_id, AIRisk.org_id == org_id))
            .all()
        )
        
        if len(risks) < 3:
            issues.append({
                "id": "low_risk_coverage",
                "severity": "medium",
                "title": "Low risk coverage",
                "description": f"Only {len(risks)} risks identified (recommended: ≥3 for audit-grade)",
                "action": "Add more risks",
                "action_url": f"/systems/{system_id}/risks"
            })
        
        # Check evidence coverage
        evidence = (
            self.db.query(Evidence)
            .filter(and_(Evidence.system_id == system_id, Evidence.org_id == org_id))
            .all()
        )
        
        if not evidence:
            issues.append({
                "id": "no_evidence_uploaded",
                "severity": "medium",
                "title": "No evidence uploaded",
                "description": "No evidence documents have been uploaded for this system",
                "action": "Upload evidence",
                "action_url": f"/systems/{system_id}/evidence"
            })
        
        # Check role-specific requirements (provider + high-risk)
        if system.eu_db_required_computed:
            if not pmm or pmm.eu_db_status != 'registered':
                issues.append({
                    "id": "eu_db_required",
                    "severity": "high",
                    "title": "EU Database registration required",
                    "description": "Provider of high-risk AI system must register in EU database",
                    "action": "Register in EU database",
                    "action_url": "https://ai-database.ec.europa.eu/"
                })
        
        return issues
    
    def get_issue_summary(self, system_id: int, org_id: int) -> Dict[str, Any]:
        """Get summary of blocking issues."""
        issues = self.get_blocking_issues(system_id, org_id)
        
        critical_count = len([i for i in issues if i['severity'] == 'critical'])
        high_count = len([i for i in issues if i['severity'] == 'high'])
        medium_count = len([i for i in issues if i['severity'] == 'medium'])
        
        return {
            "total_issues": len(issues),
            "critical_issues": critical_count,
            "high_issues": high_count,
            "medium_issues": medium_count,
            "can_export": critical_count == 0 and high_count == 0,
            "issues": issues
        }
    
    def is_export_blocked(self, system_id: int, org_id: int) -> bool:
        """Check if export is blocked due to critical/high issues."""
        summary = self.get_issue_summary(system_id, org_id)
        return not summary["can_export"]
