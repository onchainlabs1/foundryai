"""
Service for generating Statement of Applicability (SoA) exports.
"""
import csv
import io
from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from app.models import AISystem, Control, Evidence


def generate_soa_csv(system_id: int, org_id: int, db: Session) -> str:
    """
    Generate SoA CSV for a system.
    
    Returns CSV string with columns:
    - ISO Clause
    - Control Name
    - Applicable
    - Justification/Rationale
    - Owner
    - Status
    - Due Date
    - Evidence Link
    """
    
    # Get system
    system = db.query(AISystem).filter(
        AISystem.id == system_id,
        AISystem.org_id == org_id
    ).first()
    
    if not system:
        raise ValueError(f"System {system_id} not found")
    
    # Get all controls for this system
    controls = db.query(Control).filter(
        Control.system_id == system_id,
        Control.org_id == org_id
    ).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "ISO/IEC 42001 Clause",
        "Control Name",
        "Applicable",
        "Justification/Rationale",
        "Owner Email",
        "Implementation Status",
        "Due Date",
        "Evidence Links"
    ])
    
    # Write control rows
    for control in controls:
        # Get evidence for this control
        evidence_list = db.query(Evidence).filter(
            Evidence.control_id == control.id,
            Evidence.org_id == org_id
        ).all()
        
        evidence_links = ", ".join([
            f"{e.label} (v{e.version or '1'})" for e in evidence_list
        ]) if evidence_list else "No evidence uploaded"
        
        writer.writerow([
            control.iso_clause or "N/A",
            control.name,
            "Yes" if control.status != "missing" else "No",
            control.rationale or "N/A",
            control.owner_email or "Unassigned",
            control.status.upper(),
            control.due_date.isoformat() if control.due_date else "Not set",
            evidence_links
        ])
    
    # Get CSV string
    csv_content = output.getvalue()
    output.close()
    
    return csv_content


def generate_soa_markdown(system_id: int, org_id: int, db: Session) -> str:
    """
    Generate SoA as Markdown table.
    """
    
    # Get system
    system = db.query(AISystem).filter(
        AISystem.id == system_id,
        AISystem.org_id == org_id
    ).first()
    
    if not system:
        raise ValueError(f"System {system_id} not found")
    
    # Get all controls for this system
    controls = db.query(Control).filter(
        Control.system_id == system_id,
        Control.org_id == org_id
    ).all()
    
    # Build markdown table
    md = f"# Statement of Applicability\n\n"
    md += f"**System**: {system.name}\n\n"
    md += f"**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
    md += "---\n\n"
    
    md += "| ISO Clause | Control | Applicable | Status | Owner | Due Date |\n"
    md += "|------------|---------|------------|--------|-------|----------|\n"
    
    for control in controls:
        applicable = "✅ Yes" if control.status != "missing" else "❌ No"
        status_emoji = {
            "implemented": "✅",
            "partial": "🟡",
            "missing": "❌"
        }.get(control.status, "❓")
        
        md += f"| {control.iso_clause or 'N/A'} | {control.name} | {applicable} | "
        md += f"{status_emoji} {control.status.upper()} | "
        md += f"{control.owner_email or 'Unassigned'} | "
        md += f"{control.due_date.isoformat() if control.due_date else 'Not set'} |\n"
    
    md += "\n---\n\n"
    md += f"**Total Controls**: {len(controls)}\n"
    md += f"**Implemented**: {sum(1 for c in controls if c.status == 'implemented')}\n"
    md += f"**Partial**: {sum(1 for c in controls if c.status == 'partial')}\n"
    md += f"**Missing**: {sum(1 for c in controls if c.status == 'missing')}\n"
    
    return md

