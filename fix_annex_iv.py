#!/usr/bin/env python3
"""
Script para corrigir definitivamente o problema do Annex IV
"""

import sys
import os
sys.path.append('/Users/fabio/Desktop/foundry/backend')

from app.database import get_db
from app.models import Organization, AISystem
from app.services.document_generator import DocumentGenerator
import zipfile
import hashlib
import json
from datetime import datetime, timezone
from io import BytesIO

def generate_complete_annex_iv(system_id=1):
    """Gera o Annex IV completo com todos os documentos"""
    
    db = next(get_db())
    system = db.query(AISystem).filter(AISystem.id == system_id).first()
    org = db.query(Organization).first()
    
    if not system or not org:
        print("❌ Sistema ou organização não encontrados")
        return None
    
    print(f"✅ Gerando Annex IV para sistema: {system.name}")
    
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

        # Generate manifest.json
        manifest = {
            "system_id": system_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator_version": "2.0.0",
            "artifacts": artifacts,
            "approvals": [],
            "sources": []
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
    output_path = f"/Users/fabio/Desktop/foundry/annex-iv-COMPLETO-{system_id}.zip"
    with open(output_path, 'wb') as f:
        f.write(zip_content)
    
    print(f"✅ Annex IV gerado com sucesso!")
    print(f"📁 Arquivo: {output_path}")
    print(f"📊 Tamanho: {len(zip_content)} bytes")
    print(f"📄 Documentos: {len(artifacts)} arquivos")
    
    return output_path

if __name__ == "__main__":
    generate_complete_annex_iv()
