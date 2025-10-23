"""
Pytest configuration and shared fixtures for all tests.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.models import Organization, AISystem

# Use in-memory SQLite for faster tests
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
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

