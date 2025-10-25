#!/usr/bin/env python3
"""
Generate Golden ZIP fixture for Credit Scoring AI scenario.
This script creates a complete Annex IV export with realistic data.
"""

import json
import os
import sys
import tempfile
import hashlib
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Organization, AISystem

# Set environment variables
os.environ["SECRET_KEY"] = "dev-secret-key-for-development-only"

# Create in-memory SQLite database
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    """Override get_db dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

API_KEY = "dev-aims-demo-key"
HEADERS = {"X-API-Key": API_KEY}


def create_sample_pdf_content(filename, description):
    """Create sample PDF content for testing."""
    # This is a minimal PDF structure for testing
    pdf_content = f"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
({filename}: {description}) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
297
%%EOF"""
    return pdf_content.encode('utf-8')


def load_scenario():
    """Load credit scoring AI scenario data."""
    scenario_path = Path(__file__).parent / "credit_scoring_ai.json"
    with open(scenario_path, 'r') as f:
        return json.load(f)


def create_test_evidences(system_id, evidences):
    """Create sample evidence files."""
    evidence_ids = []
    
    for evidence in evidences:
        filename = evidence["filename"]
        description = evidence["description"]
        
        # Create sample PDF content
        pdf_content = create_sample_pdf_content(filename, description)
        
        # Upload evidence
        response = client.post(
            f"/evidence/{system_id}",
            files={"file": (filename, pdf_content, "application/pdf")},
            data={
                "label": description,
                "iso42001_clause": "5.1",
                "control_name": "Test Control"
            },
            headers=HEADERS
        )
        
        if response.status_code == 200:
            evidence_ids.append(response.json()["id"])
            print(f"✓ Created evidence: {filename}")
        else:
            print(f"✗ Failed to create evidence {filename}: {response.status_code}")
    
    return evidence_ids


def seed_full_system():
    """Seed complete system with all artifacts."""
    # Setup database
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    
    db = TestingSessionLocal()
    try:
        # Create test organization
        org = Organization(
            name="Credit Scoring AI Organization",
            api_key=API_KEY
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        
        # Load scenario
        scenario = load_scenario()
        
        # Create system
        system_data = scenario["system"]
        response = client.post("/systems", json=system_data, headers=HEADERS)
        
        if response.status_code != 200:
            raise Exception(f"Failed to create system: {response.status_code}")
        
        system_id = response.json()["id"]
        print(f"✓ Created system: {system_data['name']} (ID: {system_id})")
        
        # Create evidence files
        evidence_ids = create_test_evidences(system_id, scenario["evidences"])
        
        # Submit FRIA
        fria_data = {
            "system_id": system_id,
            **scenario["fria"]
        }
        
        response = client.post(f"/systems/{system_id}/fria", json=fria_data, headers=HEADERS)
        if response.status_code == 200:
            print("✓ Submitted FRIA")
        else:
            print(f"✗ Failed to submit FRIA: {response.status_code}")
        
        # Create controls
        for control in scenario["controls"]:
            control_data = {
                "system_id": system_id,
                "iso_clause": control["iso_clause"],
                "name": f"Control for {control['iso_clause']}",
                "priority": control["priority"],
                "status": control["status"],
                "owner_email": "compliance@company.com",
                "due_date": "2024-12-31",
                "rationale": f"Required for {control['iso_clause']}"
            }
            
            response = client.post("/controls/bulk", json={"controls": [control_data]}, headers=HEADERS)
            if response.status_code == 200:
                print(f"✓ Created control: {control['iso_clause']}")
            else:
                print(f"✗ Failed to create control {control['iso_clause']}: {response.status_code}")
        
        # Log incident
        incident_data = {
            "system_id": system_id,
            **scenario["incident"]
        }
        
        response = client.post("/incidents", json=incident_data, headers=HEADERS)
        if response.status_code == 200:
            print("✓ Logged incident")
        else:
            print(f"✗ Failed to log incident: {response.status_code}")
        
        return system_id
        
    finally:
        db.close()


def generate_golden_zip():
    """Generate the golden ZIP file."""
    print("🚀 Generating Golden ZIP for Credit Scoring AI scenario...")
    
    # Seed the system
    system_id = seed_full_system()
    
    # Generate Annex IV ZIP
    print(f"📦 Generating Annex IV ZIP for system {system_id}...")
    response = client.get(f"/reports/annex-iv/{system_id}", headers=HEADERS)
    
    if response.status_code != 200:
        raise Exception(f"Failed to generate Annex IV ZIP: {response.status_code}")
    
    # Save ZIP file
    fixtures_dir = Path(__file__).parent
    zip_path = fixtures_dir / "credit_scoring_ai.zip"
    
    with open(zip_path, 'wb') as f:
        f.write(response.content)
    
    print(f"✅ Golden ZIP saved to: {zip_path}")
    
    # Generate checksums
    checksums = {}
    with open(zip_path, 'rb') as f:
        content = f.read()
        checksums["credit_scoring_ai.zip"] = {
            "sha256": hashlib.sha256(content).hexdigest(),
            "size_bytes": len(content)
        }
    
    # Save checksums
    checksums_path = fixtures_dir / "checksums.txt"
    with open(checksums_path, 'w') as f:
        f.write("# Golden ZIP Checksums\n")
        f.write("# Generated by generate_golden_zip.py\n\n")
        for filename, info in checksums.items():
            f.write(f"{filename}:\n")
            f.write(f"  SHA256: {info['sha256']}\n")
            f.write(f"  Size: {info['size_bytes']} bytes\n\n")
    
    print(f"✅ Checksums saved to: {checksums_path}")
    
    # Extract and list contents for verification
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        files = zip_file.namelist()
        print(f"📋 ZIP contains {len(files)} files:")
        for file in sorted(files):
            print(f"  - {file}")
    
    return zip_path


if __name__ == "__main__":
    try:
        zip_path = generate_golden_zip()
        print(f"\n🎉 Golden ZIP generation completed successfully!")
        print(f"📁 Location: {zip_path}")
        print(f"📊 Use this file for testing ZIP completeness and manifest validation.")
        
    except Exception as e:
        print(f"❌ Error generating Golden ZIP: {e}")
        sys.exit(1)
