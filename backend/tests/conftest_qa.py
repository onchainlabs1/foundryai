"""
Shared fixtures for QA tests (T1-T8) with proper isolation.
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app


@pytest.fixture(scope="function")
def isolated_db_override():
    """
    Isolated database override that restores original after use.
    Each test gets its own in-memory database.
    """
    # Store original dependency
    original_get_db = app.dependency_overrides.get(get_db)
    
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
    
    # Apply override
    app.dependency_overrides[get_db] = override_get_db
    
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    yield test_engine, TestingSessionLocal
    
    # Cleanup: restore original dependency
    if original_get_db is not None:
        app.dependency_overrides[get_db] = original_get_db
    else:
        app.dependency_overrides.pop(get_db, None)
    
    # Drop tables
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def clean_test_environment():
    """
    Ensure clean test environment with proper SECRET_KEY.
    """
    # Set required environment variables
    os.environ["SECRET_KEY"] = "dev-secret-key-for-development-only"
    
    yield
    
    # Cleanup environment if needed
    pass


@pytest.fixture
def with_isolated_client():
    """
    Provides an isolated TestClient with clean database override.
    Returns (client, db_session) with automatic cleanup.
    """
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
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
        yield client, db_session
    finally:
        db_session.close()
        # Restore original dependency
        if original_get_db is not None:
            app.dependency_overrides[get_db] = original_get_db
        else:
            app.dependency_overrides.pop(get_db, None)
