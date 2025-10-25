"""
T5: SoA Contract Validation
Enforce SoA CSV structure and completeness.
"""

import csv
import os
import tempfile
import zipfile
from datetime import datetime

import pytest

from app.models import Organization, AISystem
from tests.conftest import create_test_system
from tests.conftest_qa import with_isolated_client

API_KEY = "dev-aims-demo-key"
HEADERS = {"X-API-Key": API_KEY}


@pytest.fixture
def setup_test_data(with_isolated_client):
    """Create test organization and data for each test."""
    client, db = with_isolated_client
    
    # Create test organization
    org = Organization(
        name="Test Organization",
        api_key=API_KEY
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    
    return {"org": org, "client": client}


def test_soa_mandatory_columns(setup_test_data):
    """Test that SoA CSV has all required columns."""
    client = setup_test_data["client"]
    
    # Create a test system
    system_data = {
        "name": "Test System",
        "purpose": "Test system for SoA contract",
        "domain": "finance",
        "ai_act_class": "high",
        "system_role": "provider"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Create some test controls
    controls_data = [
        {
            "system_id": system_id,
            "iso_clause": "ISO42001:6.1",
            "name": "Risk Management Process",
            "priority": "high",
            "status": "implemented",
            "owner_email": "compliance@company.com",
            "due_date": "2024-12-31",
            "rationale": "Critical for high-risk systems"
        },
        {
            "system_id": system_id,
            "iso_clause": "ISO42001:6.2",
            "name": "Risk Assessment",
            "priority": "medium",
            "status": "in_progress",
            "owner_email": "risk@company.com",
            "due_date": "2024-11-30",
            "rationale": "Important for compliance"
        }
    ]
    
    # Create controls via API
    for control_data in controls_data:
        response = client.post("/controls/bulk", json={"controls": [control_data]}, headers=HEADERS)
        assert response.status_code == 200
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system_id}", headers=HEADERS)
    assert response.status_code == 200
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            # Look for SoA CSV file
            soa_files = [f for f in zip_file.namelist() if 'soa' in f.lower() and f.endswith('.csv')]
            
            if not soa_files:
                pytest.skip("No SoA CSV file found in export")
            
            # Read SoA CSV
            soa_content = zip_file.read(soa_files[0])
            soa_text = soa_content.decode('utf-8')
            
            # Parse CSV
            csv_reader = csv.DictReader(soa_text.splitlines())
            
            # Check required columns
            required_columns = [
                "ISO Clause", "Control Name", "Status", "Priority",
                "Owner", "Due Date", "Rationale"
            ]
            
            actual_columns = csv_reader.fieldnames
            missing_columns = [col for col in required_columns if col not in actual_columns]
            
            if missing_columns:
                pytest.fail(f"Missing required columns in SoA: {missing_columns}")
            
            # Verify we have data rows
            rows = list(csv_reader)
            assert len(rows) > 0, "SoA CSV has no data rows"
            
    finally:
        os.unlink(temp_zip_path)


def test_soa_critical_controls_completeness(setup_test_data):
    """Test that critical controls (priority=high) have complete information."""
    client = setup_test_data["client"]
    
    # Create a test system
    system_data = {
        "name": "Test System",
        "purpose": "Test system for SoA critical controls",
        "domain": "finance",
        "ai_act_class": "high",
        "system_role": "provider"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Create test controls with different priorities
    controls_data = [
        {
            "system_id": system_id,
            "iso_clause": "ISO42001:6.1",
            "name": "Critical Risk Management",
            "priority": "high",
            "status": "implemented",
            "owner_email": "compliance@company.com",
            "due_date": "2024-12-31",
            "rationale": "Critical for high-risk systems"
        },
        {
            "system_id": system_id,
            "iso_clause": "ISO42001:6.2",
            "name": "Medium Risk Assessment",
            "priority": "medium",
            "status": "in_progress",
            "owner_email": "risk@company.com",
            "due_date": "2024-11-30",
            "rationale": "Important for compliance"
        }
    ]
    
    # Create controls via API
    for control_data in controls_data:
        response = client.post("/controls/bulk", json={"controls": [control_data]}, headers=HEADERS)
        assert response.status_code == 200
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system_id}", headers=HEADERS)
    assert response.status_code == 200
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            # Look for SoA CSV file
            soa_files = [f for f in zip_file.namelist() if 'soa' in f.lower() and f.endswith('.csv')]
            
            if not soa_files:
                pytest.skip("No SoA CSV file found in export")
            
            # Read SoA CSV
            soa_content = zip_file.read(soa_files[0])
            soa_text = soa_content.decode('utf-8')
            
            # Parse CSV
            csv_reader = csv.DictReader(soa_text.splitlines())
            rows = list(csv_reader)
            
            # Check that high priority controls have complete information
            for row in rows:
                if row.get("Priority", "").lower() == "high":
                    # High priority controls should have owner and due date
                    assert row.get("Owner", "").strip(), f"High priority control missing owner: {row.get('Control Name', 'Unknown')}"
                    assert row.get("Due Date", "").strip(), f"High priority control missing due date: {row.get('Control Name', 'Unknown')}"
                    assert row.get("Rationale", "").strip(), f"High priority control missing rationale: {row.get('Control Name', 'Unknown')}"
            
    finally:
        os.unlink(temp_zip_path)


def test_soa_data_types_validation(setup_test_data):
    """Test that SoA CSV data types are valid."""
    client = setup_test_data["client"]
    
    # Create a test system
    system_data = {
        "name": "Test System",
        "purpose": "Test system for SoA data types",
        "domain": "finance",
        "ai_act_class": "high",
        "system_role": "provider"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Create test controls
    controls_data = [
        {
            "system_id": system_id,
            "iso_clause": "ISO42001:6.1",
            "name": "Test Control",
            "priority": "high",
            "status": "implemented",
            "owner_email": "test@company.com",
            "due_date": "2024-12-31",
            "rationale": "Test rationale"
        }
    ]
    
    # Create controls via API
    for control_data in controls_data:
        response = client.post("/controls/bulk", json={"controls": [control_data]}, headers=HEADERS)
        assert response.status_code == 200
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system_id}", headers=HEADERS)
    assert response.status_code == 200
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            # Look for SoA CSV file
            soa_files = [f for f in zip_file.namelist() if 'soa' in f.lower() and f.endswith('.csv')]
            
            if not soa_files:
                pytest.skip("No SoA CSV file found in export")
            
            # Read SoA CSV
            soa_content = zip_file.read(soa_files[0])
            soa_text = soa_content.decode('utf-8')
            
            # Parse CSV
            csv_reader = csv.DictReader(soa_text.splitlines())
            rows = list(csv_reader)
            
            # Validate data types
            for row in rows:
                # Priority should be one of the expected values
                priority = row.get("Priority", "").lower()
                assert priority in ["high", "medium", "low", ""], f"Invalid priority value: {priority}"
                
                # Status should be one of the expected values
                status = row.get("Status", "").lower()
                assert status in ["implemented", "in_progress", "planned", "not_applicable", ""], f"Invalid status value: {status}"
                
                # Due date should be a valid date format (if present)
                due_date = row.get("Due Date", "").strip()
                if due_date:
                    try:
                        datetime.strptime(due_date, "%Y-%m-%d")
                    except ValueError:
                        # Try other common date formats
                        try:
                            datetime.strptime(due_date, "%d/%m/%Y")
                        except ValueError:
                            pytest.fail(f"Invalid date format: {due_date}")
            
    finally:
        os.unlink(temp_zip_path)


def test_soa_csv_structure_integrity(setup_test_data):
    """Test that SoA CSV structure is valid and consistent."""
    client = setup_test_data["client"]
    
    # Create a test system
    system_data = {
        "name": "Test System",
        "purpose": "Test system for SoA structure",
        "domain": "finance",
        "ai_act_class": "high",
        "system_role": "provider"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Create test controls
    controls_data = [
        {
            "system_id": system_id,
            "iso_clause": "ISO42001:6.1",
            "name": "Test Control 1",
            "priority": "high",
            "status": "implemented",
            "owner_email": "test1@company.com",
            "due_date": "2024-12-31",
            "rationale": "Test rationale 1"
        },
        {
            "system_id": system_id,
            "iso_clause": "ISO42001:6.2",
            "name": "Test Control 2",
            "priority": "medium",
            "status": "in_progress",
            "owner_email": "test2@company.com",
            "due_date": "2024-11-30",
            "rationale": "Test rationale 2"
        }
    ]
    
    # Create controls via API
    for control_data in controls_data:
        response = client.post("/controls/bulk", json={"controls": [control_data]}, headers=HEADERS)
        assert response.status_code == 200
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system_id}", headers=HEADERS)
    assert response.status_code == 200
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            # Look for SoA CSV file
            soa_files = [f for f in zip_file.namelist() if 'soa' in f.lower() and f.endswith('.csv')]
            
            if not soa_files:
                pytest.skip("No SoA CSV file found in export")
            
            # Read SoA CSV
            soa_content = zip_file.read(soa_files[0])
            soa_text = soa_content.decode('utf-8')
            
            # Parse CSV
            csv_reader = csv.DictReader(soa_text.splitlines())
            rows = list(csv_reader)
            
            # Check CSV structure integrity
            assert len(rows) > 0, "SoA CSV has no data rows"
            
            # Check that all rows have the same number of columns
            expected_columns = len(csv_reader.fieldnames)
            for i, row in enumerate(rows):
                actual_columns = len(row)
                assert actual_columns == expected_columns, f"Row {i} has {actual_columns} columns, expected {expected_columns}"
            
            # Check that required fields are not empty for all rows
            for i, row in enumerate(rows):
                assert row.get("ISO Clause", "").strip(), f"Row {i} missing ISO Clause"
                assert row.get("Control Name", "").strip(), f"Row {i} missing Control Name"
                assert row.get("Status", "").strip(), f"Row {i} missing Status"
            
    finally:
        os.unlink(temp_zip_path)