"""
Credit Scoring AI scenario fixtures.
Provides helper functions for creating test data.
"""

import json
import os
import sys
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


def load_scenario():
    """Load credit scoring AI scenario data."""
    scenario_path = Path(__file__).parent / "credit_scoring_ai.json"
    with open(scenario_path, 'r') as f:
        return json.load(f)


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


def create_test_evidences(system_id, db=None):
    """Create sample evidence files."""
    scenario = load_scenario()
    evidence_ids = []
    
    for evidence in scenario["evidences"]:
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
        else:
            print(f"Warning: Failed to create evidence {filename}: {response.status_code}")
    
    return evidence_ids


def seed_full_system(db, org_id):
    """Seed complete system with all artifacts."""
    scenario = load_scenario()
    
    # Create system
    system_data = scenario["system"]
    response = client.post("/systems", json=system_data, headers=HEADERS)
    
    if response.status_code != 200:
        raise Exception(f"Failed to create system: {response.status_code}")
    
    system_id = response.json()["id"]
    
    # Create evidence files
    evidence_ids = create_test_evidences(system_id, db)
    
    # Submit FRIA
    fria_data = {
        "system_id": system_id,
        **scenario["fria"]
    }
    
    response = client.post(f"/systems/{system_id}/fria", json=fria_data, headers=HEADERS)
    if response.status_code != 200:
        print(f"Warning: Failed to submit FRIA: {response.status_code}")
    
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
        if response.status_code != 200:
            print(f"Warning: Failed to create control {control['iso_clause']}: {response.status_code}")
    
    # Log incident
    incident_data = {
        "system_id": system_id,
        **scenario["incident"]
    }
    
    response = client.post("/incidents", json=incident_data, headers=HEADERS)
    if response.status_code != 200:
        print(f"Warning: Failed to log incident: {response.status_code}")
    
    return system_id


def get_golden_zip_path():
    """Get the path to the golden ZIP file."""
    return Path(__file__).parent / "credit_scoring_ai.zip"


def get_checksums_path():
    """Get the path to the checksums file."""
    return Path(__file__).parent / "checksums.txt"
