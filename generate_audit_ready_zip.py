#!/usr/bin/env python3
"""
Script para gerar ZIP audit-ready definitivo
"""

import sys
import os
sys.path.append('/Users/fabio/Desktop/foundry/backend')

from app.database import get_db
from app.models import Organization, AISystem, Control, Evidence
from app.services.document_generator import DocumentGenerator
import zipfile
import hashlib
import json
from datetime import datetime, timezone
from io import BytesIO

def generate_audit_ready_zip(system_id=1):
    """Gera o ZIP audit-ready definitivo com TODOS os documentos"""
    
    db = next(get_db())
    system = db.query(AISystem).filter(AISystem.id == system_id).first()
    org = db.query(Organization).first()
    
    if not system or not org:
        print("❌ Sistema ou organização não encontrados")
        return None
    
    print(f"✅ Gerando ZIP audit-ready para sistema: {system.name}")
    print(f"   AI Act Class: {system.ai_act_class}")
    print(f"   Personal Data: {system.personal_data_processed}")
    print(f"   Impacts Rights: {system.impacts_fundamental_rights}")
    
    # Create zip file in memory
    zip_buffer = BytesIO()
    artifacts = []
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Generate all compliance documents using DocumentGenerator
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
        print(f"📄 Gerando {len(document_templates)} documentos...")
        for doc_type, template_file in document_templates.items():
            try:
                print(f"  - Gerando {doc_type}...")
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
                    print(f"    ✅ {doc_type}.md ({len(md_content)} chars)")
                else:
                    print(f"    ❌ {doc_type} - sem conteúdo")
                        
            except Exception as e:
                print(f"    ❌ Erro gerando {doc_type}: {e}")
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
        print("  ✅ system_info.txt")

        # Add controls as CSV
        controls = db.query(Control).filter(Control.system_id == system_id).all()
        if controls:
            # Create controls CSV
            controls_csv = "Control ID,Name,Status,Due Date,ISO Clause,Priority,Owner Email,Implementation Status,Evidence Links\n"
            for control in controls:
                evidence_links = ", ".join([f"EV-{ev.id}" for ev in control.evidence])
                controls_csv += f"{control.id},{control.name},{control.status},{control.due_date},{control.iso_clause},{control.priority},{control.owner_email or 'N/A'},{control.implementation_status or 'Not set'},{evidence_links}\n"
            
            zip_file.writestr("controls.csv", controls_csv)
            artifacts.append({
                "name": "controls.csv",
                "sha256": hashlib.sha256(controls_csv.encode()).hexdigest(),
                "bytes": len(controls_csv.encode())
            })
            print("  ✅ controls.csv")

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
                print("  ✅ evidence_manifest.csv")
        except Exception as e:
            print(f"  ⚠️  Evidências não encontradas: {e}")
            evidence = []
        
        # Generate manifest.json
        manifest = {
            "system_id": system_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator_version": "3.0.0",
            "artifacts": artifacts,
            "approvals": [],
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
        print("  ✅ manifest.json")

    zip_buffer.seek(0)
    zip_content = zip_buffer.getvalue()
    
    # Save to file
    output_path = f"/Users/fabio/Desktop/foundry/AUDIT-READY-{system_id}.zip"
    with open(output_path, 'wb') as f:
        f.write(zip_content)
    
    print(f"\n🎉 ZIP AUDIT-READY gerado com sucesso!")
    print(f"📁 Arquivo: {output_path}")
    print(f"📊 Tamanho: {len(zip_content)} bytes")
    print(f"📄 Documentos: {len(artifacts)} arquivos")
    print(f"\n📋 Documentos incluídos:")
    for artifact in artifacts:
        print(f"  - {artifact['name']} ({artifact['bytes']} bytes)")
    
    return output_path

if __name__ == "__main__":
    generate_audit_ready_zip()
