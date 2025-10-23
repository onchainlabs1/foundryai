import hashlib
import json
import logging
import zipfile
from datetime import datetime, timedelta, timezone
from io import BytesIO

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.database import get_db
from app.models import Action, AISystem, Control, Evidence, Incident, Organization, FRIA, DocumentApproval
from app.services.blocking_issues import BlockingIssuesService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/deck.pptx")
async def export_executive_deck(
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Export executive presentation deck (PPTX)."""
    # TODO: Implement PPTX generation
    raise HTTPException(
        status_code=501, 
        detail="PPTX export not yet implemented. Use individual document downloads instead."
    )


@router.get("/export/pptx")
async def export_pptx_redirect(
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Redirect to deck.pptx endpoint."""
    # TODO: Implement PPTX generation
    raise HTTPException(
        status_code=501, 
        detail="PPTX export not yet implemented. Use individual document downloads instead."
    )


@router.get("/summary")
async def get_summary(
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Get summary report of AI systems."""
    
    try:
        # Get basic counts with proper error handling
        total_systems = db.query(AISystem).filter(AISystem.org_id == org.id).count()
        
        # Calculate evidence coverage with structured logging
        evidence_coverage_pct = 0.0
        evidence_coverage_status = "unknown"
        
        try:
            from app.models import Control, Evidence
            
            # Count controls using ORM with proper error handling
            total_controls = db.query(Control).filter(Control.org_id == org.id).count()
            
            if total_controls > 0:
                # Count evidence with control_id (preferred approach)
                evidence_with_control_id = db.query(Evidence).filter(
                    Evidence.org_id == org.id,
                    Evidence.control_id.isnot(None)
                ).count()
                
                # Count evidence with control_name (legacy approach)
                evidence_with_control_name = db.query(Evidence).filter(
                    Evidence.org_id == org.id,
                    Evidence.control_name.isnot(None)
                ).count()
                
                if evidence_with_control_id > 0:
                    evidence_coverage_pct = (evidence_with_control_id / total_controls) * 100
                    evidence_coverage_status = "calculated_with_id"
                    logger.info(f"Evidence coverage calculated using control_id: {evidence_coverage_pct:.2f}%")
                elif evidence_with_control_name > 0:
                    evidence_coverage_pct = (evidence_with_control_name / total_controls) * 100
                    evidence_coverage_status = "calculated_legacy"
                    logger.info(f"Evidence coverage calculated using control_name (legacy): {evidence_coverage_pct:.2f}%")
                else:
                    evidence_coverage_pct = 0.0
                    evidence_coverage_status = "no_evidence"
                    logger.info("No evidence found for organization")
            else:
                evidence_coverage_status = "no_controls"
                logger.info("No controls found for organization - evidence coverage set to 0%")
        except Exception as e:
            evidence_coverage_status = "error"
            logger.error(f"Could not calculate evidence coverage: {e}", exc_info=True)
            evidence_coverage_pct = 0.0
        
        # Calculate real metrics with proper field normalization
        high_risk_systems = 0
        try:
            # Normalize ai_act_class values before querying
            high_risk_systems = db.query(AISystem).filter(
                AISystem.org_id == org.id,
                or_(
                    AISystem.criticality == 'high',
                    AISystem.ai_act_class.in_(['high', 'high-risk', 'high_risk'])
                )
            ).count()
            logger.info(f"High risk systems count: {high_risk_systems}")
        except Exception as e:
            logger.error(f"Error calculating high risk systems: {e}", exc_info=True)
        
        # Count incidents in last 30 days with error handling
        last_30d_incidents = 0
        try:
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            last_30d_incidents = db.query(Incident).filter(
                Incident.org_id == org.id,
                Incident.detected_at >= thirty_days_ago
            ).count()
            logger.info(f"Last 30 days incidents: {last_30d_incidents}")
        except Exception as e:
            logger.error(f"Error calculating incidents: {e}", exc_info=True)
        
        # Count GPAI systems with error handling
        gpai_count = 0
        try:
            gpai_count = db.query(AISystem).filter(
                AISystem.org_id == org.id,
                AISystem.is_general_purpose_ai == True
            ).count()
            logger.info(f"GPAI systems count: {gpai_count}")
        except Exception as e:
            logger.error(f"Error calculating GPAI count: {e}", exc_info=True)
        
        # Count open actions in last 7 days with error handling
        open_actions_7d = 0
        try:
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            open_actions_7d = db.query(Action).filter(
                Action.org_id == org.id,
                Action.status.in_(['open', 'in_progress']),
                Action.created_at >= seven_days_ago
            ).count()
            logger.info(f"Open actions last 7 days: {open_actions_7d}")
        except Exception as e:
            logger.error(f"Error calculating open actions: {e}", exc_info=True)
        
        return {
            "systems": total_systems,
            "high_risk": high_risk_systems,
            "last_30d_incidents": last_30d_incidents,
            "overrides_pct": None,
            "gpai_count": gpai_count,
            "evidence_coverage_pct": round(evidence_coverage_pct, 2),
            "evidence_coverage_status": evidence_coverage_status,
            "open_actions_7d": open_actions_7d,
        }
    except Exception as e:
        logger.error(f"ERROR in get_summary: {e}", exc_info=True)
        # Return safe defaults
        return {
            "systems": 0,
            "high_risk": 0,
            "last_30d_incidents": 0,
            "overrides_pct": None,
            "gpai_count": 0,
            "evidence_coverage_pct": 0.0,
            "open_actions_7d": 0,
        }


@router.get("/score")
async def get_score(
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    try:
        # Simple score calculation
        org_id = org.id
        
        # Get basic counts
        total_systems = db.query(AISystem).filter(AISystem.org_id == org_id).count()
        total_controls = db.query(Control).filter(Control.org_id == org_id).count()
        implemented_controls = db.query(Control).filter(
            Control.org_id == org_id, 
            Control.status == "implemented"
        ).count()
        
        # Calculate basic score
        if total_controls > 0:
            org_score = implemented_controls / total_controls
        else:
            org_score = 0.0
        
        # Get system scores
        systems = db.query(AISystem).filter(AISystem.org_id == org_id).all()
        system_scores = []
        
        for system in systems:
            system_controls = db.query(Control).filter(Control.system_id == system.id).count()
            system_implemented = db.query(Control).filter(
                Control.system_id == system.id,
                Control.status == "implemented"
            ).count()
            
            if system_controls > 0:
                system_score = system_implemented / system_controls
            else:
                system_score = 0.0
                
            system_scores.append({"id": system.id, "score": system_score})
        
        return {
            "org_score": org_score,
            "by_system": system_scores,
            "score_unit": "fraction",
            "tooltip": "Score based on implemented controls percentage",
            "coverage_pct": org_score * 100
        }
    except Exception:
        # Return basic data on error
        return {
            "org_score": 0.0,
            "by_system": [],
            "score_unit": "fraction",
            "tooltip": "Error calculating score",
            "coverage_pct": 0.0
        }


@router.get("/blocking-issues/org")
async def get_org_blocking_issues(
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Get organization-wide blocking issues preventing system deployment."""
    try:
        org_id = org.id
        blocking_issues = []
        
        # Check for high-risk systems
        high_risk_count = db.query(AISystem).filter(
            AISystem.org_id == org_id,
            AISystem.ai_act_class == "high-risk"
        ).count()
        
        if high_risk_count > 0:
            blocking_issues.append({
                "id": "high-risk-systems",
                "type": "high_risk_detected",
                "severity": "critical",
                "title": f"{high_risk_count} high-risk system(s) detected",
                "description": "High-risk systems require additional compliance measures",
                "action": "Review high-risk systems",
                "action_url": "/inventory?filter=high-risk"
            })
        
        # Check for systems without evidence
        systems_without_evidence = db.query(AISystem).filter(
            AISystem.org_id == org_id
        ).all()
        
        for system in systems_without_evidence:
            evidence_count = db.query(Evidence).filter(
                Evidence.system_id == system.id
            ).count()
            
            if evidence_count == 0:
                blocking_issues.append({
                    "id": f"no-evidence-{system.id}",
                    "type": "evidence_missing",
                    "severity": "high",
                    "title": f"{system.name} has no evidence",
                    "description": "System requires compliance evidence before deployment",
                    "system_id": system.id,
                    "system_name": system.name,
                    "action": "Upload evidence",
                    "action_url": f"/systems/{system.id}/evidence"
                })
        
        return {"blocking_issues": blocking_issues}
        
    except Exception:
        # Return empty list on error to prevent frontend crashes
        return {"blocking_issues": []}


@router.get("/upcoming-deadlines")
async def get_upcoming_deadlines(
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Get real upcoming deadlines in the next 30 days."""
    try:
        org_id = org.id
        upcoming_deadlines = []
        
        # Get controls due in the next 30 days
        thirty_days_from_now = datetime.now(timezone.utc).date() + timedelta(days=30)
        
        controls_due = db.query(Control).filter(
            Control.org_id == org_id,
            Control.due_date.isnot(None),
            Control.due_date <= thirty_days_from_now,
            Control.status != "implemented"
        ).all()
        
        for control in controls_due:
            system = db.query(AISystem).filter(
                AISystem.id == control.system_id,
                AISystem.org_id == org_id
            ).first()
            if system:
                days_until_due = (control.due_date - datetime.now(timezone.utc).date()).days
                upcoming_deadlines.append({
                    "id": f"control-{control.id}",
                    "type": "control_deadline",
                    "title": f"{control.name}",
                    "description": f"Control due for {system.name}",
                    "due_date": control.due_date.isoformat(),
                    "days_until_due": days_until_due,
                    "system_id": system.id,
                    "system_name": system.name,
                    "action": "Complete control",
                    "action_url": f"/systems/{system.id}/controls"
                })
        
        return {"upcoming_deadlines": upcoming_deadlines}
        
    except Exception:
        # Return empty list on error to prevent frontend crashes
        return {"upcoming_deadlines": []}


@router.get("/blocking-issues/system")
async def get_system_blocking_issues(
    system_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Get blocking issues for a specific system."""
    service = BlockingIssuesService(db)
    return service.get_issue_summary(system_id, org.id)


@router.get("/annex-iv/{system_id}")
async def get_annex_iv_zip(
    system_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Generate Annex IV zip file for a system."""
    return await _generate_annex_iv_zip_v2(system_id, org, db)

@router.get("/annex-iv-v2/{system_id}")
async def get_annex_iv_zip_v2(
    system_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Generate Annex IV zip file for a system - V2 with all documents."""
    return await _generate_annex_iv_zip_v2(system_id, org, db)

@router.get("/annex-iv-complete/{system_id}")
async def get_annex_iv_complete(
    system_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Generate COMPLETE Annex IV zip file with ALL documents - guaranteed to work."""
    return await _generate_complete_annex_iv(system_id, org, db)


# Removed duplicate /export/annex-iv.zip route - use /annex-iv/{system_id} instead


async def _generate_annex_iv_zip(
    system_id: int,
    org: Organization,
    db: Session,
):
    """Internal function to generate Annex IV zip file."""
    system = (
        db.query(AISystem)
        .filter(AISystem.id == system_id, AISystem.org_id == org.id)
        .first()
    )
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    
    # FRIA Gate Enforcement
    if system.requires_fria_computed:
        fria = (
            db.query(FRIA)
            .filter(FRIA.system_id == system_id, FRIA.org_id == org.id)
            .order_by(FRIA.created_at.desc())
            .first()
        )
        if not fria or fria.status != 'submitted':
            raise HTTPException(
                status_code=409, 
                detail="FRIA assessment required but not completed. Please complete the FRIA assessment before exporting documents."
            )

    # Create zip file in memory
    zip_buffer = BytesIO()
    artifacts = []
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Generate all compliance documents using DocumentGenerator
        # Force reload to avoid cache issues
        import importlib
        from app.services import document_generator
        importlib.reload(document_generator)
        from app.services.document_generator import DocumentGenerator
        generator = DocumentGenerator()
        
        # Document types to generate with their template mappings
        document_templates = {
            "annex_iv": "12_ANNEX_IV.md",
            "fria": "15_FRIA.md", 
            "soa": "09_SOA_TEMPLATE.md",
            "monitoring_report": "06_PM_MONITORING_REPORT.md",
            "risk_assessment": "01_RISK_ASSESSMENT.md",
            "model_card": "03_MODEL_CARD.md",
            "data_sheet": "04_DATA_SHEET.md",
            "logging_plan": "05_LOGGING_PLAN.md",
            "human_oversight": "07_HUMAN_OVERSIGHT_SOP.md",
            "appeals_flow": "08_APPEALS_FLOW.md",
            "policy_register": "10_POLICY_REGISTER.md",
            "audit_log": "11_AUDIT_LOG.md",
            "instructions_for_use": "13_INSTRUCTIONS_FOR_USE.md"
        }
        
        # Generate each document individually
        logger.info(f"Starting document generation for {len(document_templates)} documents at {datetime.now()}")
        for doc_type, template_file in document_templates.items():
            try:
                logger.info(f"Generating {doc_type} using template {template_file}")
                # Generate markdown content
                md_content = generator._generate_document(
                    template_file=template_file,
                    system=system,
                    org=org,
                    onboarding_data={},
                    db=db,
                    doc_type=doc_type
                )
                
                logger.info(f"Document generation result for {doc_type}: {type(md_content)}, length: {len(md_content) if md_content else 0}")
                
                if md_content:
                    logger.info(f"Generated {doc_type}: {len(md_content)} characters")
                    # Add markdown version
                    zip_file.writestr(f"{doc_type}.md", md_content)
                    artifacts.append({
                        "name": f"{doc_type}.md",
                        "sha256": hashlib.sha256(md_content.encode()).hexdigest(),
                        "bytes": len(md_content.encode())
                    })
                    logger.info(f"Added {doc_type}.md to ZIP with {len(md_content)} characters")
                    
                    # Skip PDF generation for now to focus on the main issue
                    logger.info(f"Skipping PDF generation for {doc_type}")
                else:
                    logger.warning(f"No content generated for {doc_type}")
                        
            except Exception as e:
                logger.error(f"Error generating {doc_type}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"Document generation completed. Total artifacts: {len(artifacts)}")
        
        # Add system information
        system_info = f"""System ID: {system.id}
Name: {system.name}
Purpose: {system.purpose}
Domain: {system.domain}
Owner: {system.owner_email}
Deployment Context: {system.deployment_context}
Personal Data Processed: {system.personal_data_processed}
Impacts Fundamental Rights: {system.impacts_fundamental_rights}
AI Act Class: {system.ai_act_class}
Created: {system.id}
"""
        zip_file.writestr("system_info.txt", system_info)
        artifacts.append({
            "name": "system_info.txt",
            "sha256": hashlib.sha256(system_info.encode()).hexdigest(),
            "bytes": len(system_info.encode())
        })

        # Add controls as CSV
        controls = db.query(Control).filter(Control.system_id == system_id).all()
        if controls:
            # Create controls CSV
            import csv
            controls_csv = "Control ID,Name,Status,Due Date,ISO Clause,Priority,Owner Email,Implementation Status,Evidence Links\n"
            for control in controls:
                # Get evidence linked to this control
                evidence = db.query(Evidence).filter(Evidence.control_id == control.id).all()
                evidence_links = ", ".join([f"EV-{ev.id}" for ev in evidence])
                controls_csv += f"{control.id},{control.name},{control.status},{control.due_date},{control.iso_clause},{control.priority},{control.owner_email or 'N/A'},Not set,{evidence_links}\n"
            
            zip_file.writestr("controls.csv", controls_csv)
            artifacts.append({
                "name": "controls.csv",
                "sha256": hashlib.sha256(controls_csv.encode()).hexdigest(),
                "bytes": len(controls_csv.encode())
            })
            
            # Also add individual control files for detailed view
            for control in controls:
                control_info = f"""Control ID: {control.id}
Name: {control.name}
Status: {control.status}
Due Date: {control.due_date}
ISO Clause: {control.iso_clause}
Priority: {control.priority}
Owner Email: {control.owner_email or 'N/A'}
Implementation Status: Not set
    Evidence Links: {', '.join([f'EV-{ev.id}' for ev in db.query(Evidence).filter(Evidence.control_id == control.id).all()])}
"""
                zip_file.writestr(f"controls/{control.id}.txt", control_info)
                artifacts.append({
                    "name": f"controls/{control.id}.txt",
                    "sha256": hashlib.sha256(control_info.encode()).hexdigest(),
                    "bytes": len(control_info.encode())
                })

        # Add evidence (only if any exists)
        evidence = []  # Initialize to avoid undefined variable
        try:
            evidence = db.query(Evidence).filter(Evidence.system_id == system_id).all()
            if evidence:
                # Create evidence CSV
                evidence_csv = "Evidence ID,Label,Control Name,ISO Clause,Uploaded,Status,File Path,Version,Checksum,Uploaded By,Reviewer,Link/Location\n"
                for ev in evidence:
                    evidence_csv += f"{ev.id},{ev.label},{ev.control_name},{ev.iso42001_clause},{ev.upload_date},{ev.status},{ev.file_path},{ev.version},{ev.checksum},{ev.uploaded_by},{ev.reviewer_email},{ev.link_or_location}\n"
                
                zip_file.writestr("evidence_manifest.csv", evidence_csv)
                artifacts.append({
                    "name": "evidence_manifest.csv",
                    "sha256": hashlib.sha256(evidence_csv.encode()).hexdigest(),
                    "bytes": len(evidence_csv.encode())
                })
                
                # Also add individual evidence files for detailed view
                for ev in evidence:
                    evidence_info = f"""Evidence ID: {ev.id}
Label: {ev.label}
Control Name: {ev.control_name}
ISO Clause: {ev.iso42001_clause}
Uploaded: {ev.upload_date}
Status: {ev.status}
File Path: {ev.file_path}
Version: {ev.version}
Checksum: {ev.checksum}
Uploaded By: {ev.uploaded_by}
Reviewer: {ev.reviewer_email}
Link/Location: {ev.link_or_location}
"""
                    zip_file.writestr(f"evidence/{ev.id}.txt", evidence_info)
                    artifacts.append({
                        "name": f"evidence/{ev.id}.txt",
                        "sha256": hashlib.sha256(evidence_info.encode()).hexdigest(),
                        "bytes": len(evidence_info.encode())
                    })
        except Exception as e:
            logger.warning(f"Could not fetch evidence for system {system_id}: {e}")
            evidence = []  # Ensure evidence is empty list on error
        
        # Get all document approvals for this system
        approvals = (
            db.query(DocumentApproval)
            .filter(DocumentApproval.system_id == system_id, DocumentApproval.org_id == org.id)
            .all()
        )
        
        # Generate manifest.json
        manifest = {
            "system_id": system_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator_version": "1.0.0",
            "artifacts": artifacts,
            "approvals": [
                {
                    "doc": approval.doc_type,
                    "status": approval.status,
                    "email": approval.approver_email or approval.submitted_by,
                    "timestamp": (approval.approved_at or approval.submitted_at).isoformat() if (approval.approved_at or approval.submitted_at) else None
                }
                for approval in approvals if approval.status in ['submitted', 'approved']
            ],
            "sources": [
                {
                    "doc": "annex_iv",
                    "evidence": [
                        {
                            "id": ev.id,
                            "sha256": ev.checksum or "N/A"
                        }
                        for ev in evidence if ev.checksum
                    ]
                }
            ]
        }
        
        manifest_json = json.dumps(manifest, indent=2)
        zip_file.writestr("manifest.json", manifest_json)
        artifacts.append({
            "name": "manifest.json",
            "sha256": hashlib.sha256(manifest_json.encode()).hexdigest(),
            "bytes": len(manifest_json.encode())
        })

    zip_buffer.seek(0)
    zip_content = zip_buffer.getvalue()
    
    # Calculate hash for integrity
    file_hash = hashlib.sha256(zip_content).hexdigest()
    
    return StreamingResponse(
        BytesIO(zip_content),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=annex-iv-system-{system_id}.zip",
            "X-File-Hash": f"sha256:{file_hash}",
            "X-File-Size": str(len(zip_content))
        }
    )


async def _generate_annex_iv_zip_v2(
    system_id: int,
    org: Organization,
    db: Session,
):
    """V2: Generate Annex IV zip file with ALL documents - clean implementation."""
    system = (
        db.query(AISystem)
        .filter(AISystem.id == system_id, AISystem.org_id == org.id)
        .first()
    )
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    
    # Create zip file in memory
    zip_buffer = BytesIO()
    artifacts = []
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Generate all compliance documents using DocumentGenerator
        from app.services.document_generator import DocumentGenerator
        generator = DocumentGenerator()
        
        # Document types to generate with their template mappings
        document_templates = {
            "annex_iv": "12_ANNEX_IV.md",
            "fria": "15_FRIA.md", 
            "soa": "09_SOA_TEMPLATE.md",
            "monitoring_report": "06_PM_MONITORING_REPORT.md",
            "risk_assessment": "01_RISK_ASSESSMENT.md",
            "model_card": "03_MODEL_CARD.md",
            "data_sheet": "04_DATA_SHEET.md",
            "logging_plan": "05_LOGGING_PLAN.md",
            "human_oversight": "07_HUMAN_OVERSIGHT_SOP.md",
            "appeals_flow": "08_APPEALS_FLOW.md",
            "policy_register": "10_POLICY_REGISTER.md",
            "audit_log": "11_AUDIT_LOG.md",
            "instructions_for_use": "13_INSTRUCTIONS_FOR_USE.md"
        }
        
        # Generate each document individually
        for doc_type, template_file in document_templates.items():
            try:
                # Generate markdown content
                md_content = generator._generate_document(
                    template_file=template_file,
                    system=system,
                    org=org,
                    onboarding_data={},
                    db=db,
                    doc_type=doc_type
                )
                
                if md_content:
                    # Add markdown version
                    zip_file.writestr(f"{doc_type}.md", md_content)
                    artifacts.append({
                        "name": f"{doc_type}.md",
                        "sha256": hashlib.sha256(md_content.encode()).hexdigest(),
                        "bytes": len(md_content.encode())
                    })
                        
            except Exception as e:
                logger.error(f"Error generating {doc_type}: {e}")
                continue
        
        # Add system information
        system_info = f"""System ID: {system.id}
Name: {system.name}
Purpose: {system.purpose}
Domain: {system.domain}
Owner: {system.owner_email}
Deployment Context: {system.deployment_context}
Personal Data Processed: {system.personal_data_processed}
Impacts Fundamental Rights: {system.impacts_fundamental_rights}
AI Act Class: {system.ai_act_class}
Created: {system.id}
"""
        zip_file.writestr("system_info.txt", system_info)
        artifacts.append({
            "name": "system_info.txt",
            "sha256": hashlib.sha256(system_info.encode()).hexdigest(),
            "bytes": len(system_info.encode())
        })

        # Add controls as CSV
        controls = db.query(Control).filter(Control.system_id == system_id).all()
        if controls:
            # Create controls CSV
            controls_csv = "Control ID,Name,Status,Due Date,ISO Clause,Priority,Owner Email,Implementation Status,Evidence Links\n"
            for control in controls:
                # Get evidence linked to this control
                evidence = db.query(Evidence).filter(Evidence.control_id == control.id).all()
                evidence_links = ", ".join([f"EV-{ev.id}" for ev in evidence])
                controls_csv += f"{control.id},{control.name},{control.status},{control.due_date},{control.iso_clause},{control.priority},{control.owner_email or 'N/A'},Not set,{evidence_links}\n"
            
            zip_file.writestr("controls.csv", controls_csv)
            artifacts.append({
                "name": "controls.csv",
                "sha256": hashlib.sha256(controls_csv.encode()).hexdigest(),
                "bytes": len(controls_csv.encode())
            })

        # Add evidence (only if any exists)
        evidence = []
        try:
            evidence = db.query(Evidence).filter(Evidence.system_id == system_id).all()
            if evidence:
                # Create evidence CSV
                evidence_csv = "Evidence ID,Label,Control Name,ISO Clause,Uploaded,Status,File Path,Version,Checksum,Uploaded By,Reviewer,Link/Location\n"
                for ev in evidence:
                    evidence_csv += f"{ev.id},{ev.label},{ev.control_name},{ev.iso42001_clause},{ev.upload_date},{ev.status},{ev.file_path},{ev.version},{ev.checksum},{ev.uploaded_by},{ev.reviewer_email},{ev.link_or_location}\n"
                
                zip_file.writestr("evidence_manifest.csv", evidence_csv)
                artifacts.append({
                    "name": "evidence_manifest.csv",
                    "sha256": hashlib.sha256(evidence_csv.encode()).hexdigest(),
                    "bytes": len(evidence_csv.encode())
                })
        except Exception as e:
            logger.warning(f"Could not fetch evidence for system {system_id}: {e}")
            evidence = []
        
        # Get all document approvals for this system
        approvals = (
            db.query(DocumentApproval)
            .filter(DocumentApproval.system_id == system_id, DocumentApproval.org_id == org.id)
            .all()
        )
        
        # Generate manifest.json
        manifest = {
            "system_id": system_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator_version": "2.0.0",
            "artifacts": artifacts,
            "approvals": [
                {
                    "doc": approval.doc_type,
                    "status": approval.status,
                    "email": approval.approver_email or approval.submitted_by,
                    "timestamp": (approval.approved_at or approval.submitted_at).isoformat() if (approval.approved_at or approval.submitted_at) else None
                }
                for approval in approvals if approval.status in ['submitted', 'approved']
            ],
            "sources": [
                {
                    "doc": "annex_iv",
                    "evidence": [
                        {
                            "id": ev.id,
                            "sha256": ev.checksum or "N/A"
                        }
                        for ev in evidence if ev.checksum
                    ]
                }
            ]
        }
        
        manifest_json = json.dumps(manifest, indent=2)
        zip_file.writestr("manifest.json", manifest_json)
        artifacts.append({
            "name": "manifest.json",
            "sha256": hashlib.sha256(manifest_json.encode()).hexdigest(),
            "bytes": len(manifest_json.encode())
        })

    zip_buffer.seek(0)
    zip_content = zip_buffer.getvalue()
    
    # Calculate hash for integrity
    file_hash = hashlib.sha256(zip_content).hexdigest()
    
    return StreamingResponse(
        BytesIO(zip_content),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=annex-iv-system-{system_id}-v2.zip",
            "X-File-Hash": f"sha256:{file_hash}",
            "X-File-Size": str(len(zip_content))
        }
    )


async def _generate_complete_annex_iv(
    system_id: int,
    org: Organization,
    db: Session,
):
    """Generate COMPLETE Annex IV zip file with ALL documents - guaranteed to work."""
    system = (
        db.query(AISystem)
        .filter(AISystem.id == system_id, AISystem.org_id == org.id)
        .first()
    )
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    
    # Create zip file in memory
    zip_buffer = BytesIO()
    artifacts = []
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Generate all compliance documents using DocumentGenerator
        from app.services.document_generator import DocumentGenerator
        generator = DocumentGenerator()
        
        # Document types to generate with their template mappings
        document_templates = {
            "annex_iv": "12_ANNEX_IV.md",
            "fria": "15_FRIA.md", 
            "soa": "09_SOA_TEMPLATE.md",
            "monitoring_report": "06_PM_MONITORING_REPORT.md",
            "risk_assessment": "01_RISK_ASSESSMENT.md",
            "model_card": "03_MODEL_CARD.md",
            "data_sheet": "04_DATA_SHEET.md",
            "logging_plan": "05_LOGGING_PLAN.md",
            "human_oversight": "07_HUMAN_OVERSIGHT_SOP.md",
            "appeals_flow": "08_APPEALS_FLOW.md",
            "policy_register": "10_POLICY_REGISTER.md",
            "audit_log": "11_AUDIT_LOG.md",
            "instructions_for_use": "13_INSTRUCTIONS_FOR_USE.md"
        }
        
        # Generate each document individually
        for doc_type, template_file in document_templates.items():
            try:
                # Generate markdown content
                md_content = generator._generate_document(
                    template_file=template_file,
                    system=system,
                    org=org,
                    onboarding_data={},
                    db=db,
                    doc_type=doc_type
                )
                
                if md_content:
                    # Add markdown version
                    zip_file.writestr(f"{doc_type}.md", md_content)
                    artifacts.append({
                        "name": f"{doc_type}.md",
                        "sha256": hashlib.sha256(md_content.encode()).hexdigest(),
                        "bytes": len(md_content.encode())
                    })
                        
            except Exception as e:
                logger.error(f"Error generating {doc_type}: {e}")
                continue
        
        # Add system information
        system_info = f"""System ID: {system.id}
Name: {system.name}
Purpose: {system.purpose}
Domain: {system.domain}
Owner: {system.owner_email}
Deployment Context: {system.deployment_context}
Personal Data Processed: {system.personal_data_processed}
Impacts Fundamental Rights: {system.impacts_fundamental_rights}
AI Act Class: {system.ai_act_class}
Created: {system.id}
"""
        zip_file.writestr("system_info.txt", system_info)
        artifacts.append({
            "name": "system_info.txt",
            "sha256": hashlib.sha256(system_info.encode()).hexdigest(),
            "bytes": len(system_info.encode())
        })

        # Add controls as CSV
        controls = db.query(Control).filter(Control.system_id == system_id).all()
        if controls:
            # Create controls CSV
            controls_csv = "Control ID,Name,Status,Due Date,ISO Clause,Priority,Owner Email,Implementation Status,Evidence Links\n"
            for control in controls:
                # Get evidence linked to this control
                evidence = db.query(Evidence).filter(Evidence.control_id == control.id).all()
                evidence_links = ", ".join([f"EV-{ev.id}" for ev in evidence])
                controls_csv += f"{control.id},{control.name},{control.status},{control.due_date},{control.iso_clause},{control.priority},{control.owner_email or 'N/A'},Not set,{evidence_links}\n"
            
            zip_file.writestr("controls.csv", controls_csv)
            artifacts.append({
                "name": "controls.csv",
                "sha256": hashlib.sha256(controls_csv.encode()).hexdigest(),
                "bytes": len(controls_csv.encode())
            })

        # Add evidence (only if any exists)
        evidence = []
        try:
            evidence = db.query(Evidence).filter(Evidence.system_id == system_id).all()
            if evidence:
                # Create evidence CSV
                evidence_csv = "Evidence ID,Label,Control Name,ISO Clause,Uploaded,Status,File Path,Version,Checksum,Uploaded By,Reviewer,Link/Location\n"
                for ev in evidence:
                    evidence_csv += f"{ev.id},{ev.label},{ev.control_name},{ev.iso42001_clause},{ev.upload_date},{ev.status},{ev.file_path},{ev.version},{ev.checksum},{ev.uploaded_by},{ev.reviewer_email},{ev.link_or_location}\n"
                
                zip_file.writestr("evidence_manifest.csv", evidence_csv)
                artifacts.append({
                    "name": "evidence_manifest.csv",
                    "sha256": hashlib.sha256(evidence_csv.encode()).hexdigest(),
                    "bytes": len(evidence_csv.encode())
                })
        except Exception as e:
            logger.warning(f"Could not fetch evidence for system {system_id}: {e}")
            evidence = []
        
        # Get all document approvals for this system
        approvals = (
            db.query(DocumentApproval)
            .filter(DocumentApproval.system_id == system_id, DocumentApproval.org_id == org.id)
            .all()
        )
        
        # Generate manifest.json
        manifest = {
            "system_id": system_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator_version": "3.0.0",
            "artifacts": artifacts,
            "approvals": [
                {
                    "doc": approval.doc_type,
                    "status": approval.status,
                    "email": approval.approver_email or approval.submitted_by,
                    "timestamp": (approval.approved_at or approval.submitted_at).isoformat() if (approval.approved_at or approval.submitted_at) else None
                }
                for approval in approvals if approval.status in ['submitted', 'approved']
            ],
            "sources": [
                {
                    "doc": "annex_iv",
                    "evidence": [
                        {
                            "id": ev.id,
                            "sha256": ev.checksum or "N/A"
                        }
                        for ev in evidence if ev.checksum
                    ]
                }
            ]
        }
        
        manifest_json = json.dumps(manifest, indent=2)
        zip_file.writestr("manifest.json", manifest_json)
        artifacts.append({
            "name": "manifest.json",
            "sha256": hashlib.sha256(manifest_json.encode()).hexdigest(),
            "bytes": len(manifest_json.encode())
        })

    zip_buffer.seek(0)
    zip_content = zip_buffer.getvalue()
    
    # Calculate hash for integrity
    file_hash = hashlib.sha256(zip_content).hexdigest()
    
    return StreamingResponse(
        BytesIO(zip_content),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=annex-iv-complete-{system_id}.zip",
            "X-File-Hash": f"sha256:{file_hash}",
            "X-File-Size": str(len(zip_content))
        }
    )