"""
Pytest configuration and shared fixtures for all tests.
"""
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models import Organization, AISystem, AIRisk, Oversight, PMM

# Use in-memory SQLite for faster tests
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Create a fresh database session for each test.
    Creates all tables, yields session, then drops all tables for isolation.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def create_test_system(org_id: int, **kwargs) -> AISystem:
    """
    Helper function to create AISystem with all required fields.
    """
    defaults = {
        'name': 'Test System',
        'org_id': org_id,
        'ai_act_class': 'limited',
        'impacts_fundamental_rights': False,
        'personal_data_processed': False,
        'uses_biometrics': False,
        'is_general_purpose_ai': False,
        'processes_sensitive_data': False,
        'uses_gpai': False,
        'biometrics_in_public': False,
        'requires_fria': False,
    }
    defaults.update(kwargs)
    return AISystem(**defaults)


@pytest.fixture(scope="function")
def test_org_with_key(db_session: Session) -> dict:
    """
    Create a test organization with a valid API key.
    Returns dict with org_id, api_key, and headers for requests.
    """
    org = Organization(
        name="Test Organization",
        api_key="test-valid-key-12345"
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    
    return {
        "org_id": org.id,
        "api_key": org.api_key,
        "headers": {"X-API-Key": org.api_key}
    }


@pytest.fixture(scope="function")
def test_org_with_systems(db_session: Session, test_org_with_key: dict) -> dict:
    """
    Create a test organization with sample AI systems.
    Returns dict with org_id, api_key, headers, and list of system_ids.
    """
    from app.models import AISystem
    
    systems = [
        create_test_system(
            org_id=test_org_with_key["org_id"],
            name="Test High Risk System",
            purpose="Testing high-risk AI system",
            domain="testing",
            deployment_context="public",
            ai_act_class="high-risk",
            is_gpai=False,
            role="provider",
            impacts_fundamental_rights=True,
            personal_data_processed=True,
            requires_fria=True
        ),
        create_test_system(
            org_id=test_org_with_key["org_id"],
            name="Test GPAI System",
            purpose="Testing GPAI system",
            domain="testing",
            deployment_context="internal",
            ai_act_class="limited-risk",
            is_gpai=True,
            role="provider",
            is_general_purpose_ai=True,
            uses_gpai=True
        )
    ]
    
    for system in systems:
        db_session.add(system)
    db_session.commit()
    
    system_ids = [s.id for s in systems]
    
    return {
        **test_org_with_key,
        "system_ids": system_ids
    }


@pytest.fixture(scope="function")
def test_client_with_seed():
    """
    Central fixture that provides isolated TestClient with Credit Scoring AI scenario.
    This fixture:
    - Creates isolated in-memory database
    - Applies get_db override with proper teardown
    - Creates TestClient after override is applied
    - Seeds organization 'dev-aims-demo-key' and Credit Scoring scenario
    - Returns (client, db_session, org_data) with automatic cleanup
    """
    # Set required environment variables
    os.environ["SECRET_KEY"] = "dev-secret-key-for-development-only"
    
    # Create isolated test engine
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

    # Store original and apply override
    original_get_db = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    
    # Create clean tables
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    
    # Create TestClient AFTER override is applied
    client = TestClient(app)
    
    # Create a session for test data setup
    db_session = TestingSessionLocal()
    
    try:
        # Create organization with dev-aims-demo-key
        org = Organization(
            name="Test Org",
            api_key="dev-aims-demo-key"
        )
        db_session.add(org)
        db_session.commit()
        db_session.refresh(org)
        
        # Seed Credit Scoring AI scenario
        system_id = seed_credit_scoring_scenario(client, db_session, org.id)
        
        org_data = {
            "org": org,
            "org_id": org.id,
            "api_key": org.api_key,
            "headers": {"X-API-Key": org.api_key},
            "system_id": system_id
        }
        
        yield client, db_session, org_data
        
    finally:
        db_session.close()
        # Restore original dependency
        if original_get_db is not None:
            app.dependency_overrides[get_db] = original_get_db
        else:
            app.dependency_overrides.pop(get_db, None)


def seed_credit_scoring_scenario(client, db_session, org_id):
    """
    Seed the Credit Scoring AI scenario with all required data.
    Returns the system_id of the created system.
    """
    from pathlib import Path
    import json
    
    # Load scenario data
    scenario_path = Path(__file__).parent / "fixtures" / "credit_scoring_ai.json"
    if not scenario_path.exists():
        # Create minimal scenario if file doesn't exist
        scenario = {
            "system": {
                "name": "Credit Scoring AI System",
                "purpose": "Automated credit risk assessment",
                "domain": "finance",
                "deployment_context": "public",
                "ai_act_class": "high",
                "system_role": "provider",
                "impacts_fundamental_rights": True,
                "personal_data_processed": True,
                "requires_fria": True
            },
            "evidences": [
                {"filename": "risk_assessment.pdf", "description": "Risk Assessment Document"},
                {"filename": "data_protection.pdf", "description": "Data Protection Impact Assessment"},
                {"filename": "technical_docs.pdf", "description": "Technical Documentation"}
            ],
            "fria": {
                "high_risk_justification": "System processes personal financial data for automated decision making",
                "risk_mitigation": "Comprehensive risk controls and human oversight implemented"
            },
            "controls": [
                {"iso_clause": "5.1", "priority": "high", "status": "implemented"},
                {"iso_clause": "5.2", "priority": "medium", "status": "in_progress"}
            ],
            "incident": {
                "title": "Data Processing Error",
                "description": "Minor data processing error detected and resolved",
                "severity": "low",
                "status": "resolved"
            }
        }
    else:
        with open(scenario_path, 'r') as f:
            scenario = json.load(f)
    
    # Create system
    system_data = scenario["system"]
    response = client.post("/systems", json=system_data, headers={"X-API-Key": "dev-aims-demo-key"})
    
    if response.status_code != 200:
        raise Exception(f"Failed to create system: {response.status_code} - {response.text}")
    
    system_id = response.json()["id"]
    
    # Create evidence files directly in database to avoid rate limiting
    from app.models import Evidence
    import hashlib
    from datetime import datetime, timezone
    
    for i, evidence in enumerate(scenario["evidences"]):
        filename = evidence["filename"]
        description = evidence["description"]
        
        # Create sample content
        content = f"Sample content for {filename}: {description}"
        checksum = hashlib.sha256(content.encode()).hexdigest()
        
        # Create evidence directly in database
        evidence_obj = Evidence(
            org_id=org_id,
            system_id=system_id,
            label=description,
            file_path=f"/tmp/{filename}",
            checksum=checksum,
            iso42001_clause="5.1",
            control_name="Test Control",
            status="approved",
            version="1.0",
            upload_date=datetime.now(timezone.utc),
            uploaded_by="test@example.com"
        )
        db_session.add(evidence_obj)
    
    db_session.commit()
    
    # Submit FRIA
    fria_data = {
        "system_id": system_id,
        **scenario["fria"]
    }
    
    response = client.post(f"/systems/{system_id}/fria", json=fria_data, headers={"X-API-Key": "dev-aims-demo-key"})
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
        
        response = client.post("/controls/bulk", json={"controls": [control_data]}, headers={"X-API-Key": "dev-aims-demo-key"})
        if response.status_code != 200:
            print(f"Warning: Failed to create control {control['iso_clause']}: {response.status_code}")
    
    # Log incident
    incident_data = {
        "system_id": system_id,
        **scenario["incident"]
    }
    
    response = client.post("/incidents", json=incident_data, headers={"X-API-Key": "dev-aims-demo-key"})
    if response.status_code != 200:
        print(f"Warning: Failed to log incident: {response.status_code}")
    
    return system_id

