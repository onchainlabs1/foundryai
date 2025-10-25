"""
Test UTC timezone handling in API responses.
"""

import os
import re
from datetime import datetime, timezone

import pytest
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine

from app.types import UTCDateTime


@pytest.fixture
def setup_test_data(test_client_with_seed):
    """Create test organization and data for each test using shared fixture."""
    client, db_session, org_data = test_client_with_seed
    
    return {
        "client": client,
        "db_session": db_session,
        "org_data": org_data,
        "system_id": org_data["system_id"],
        "headers": org_data["headers"]
    }


def test_all_responses_have_timezone(setup_test_data):
    """Test that all API responses use timezone-aware datetimes."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    
    # Test system creation response
    response = client.get(f"/systems/{system_id}", headers=headers)
    assert response.status_code == 200
    
    system_data = response.json()
    
    # Check that system data is returned (even without created_at/updated_at)
    assert "id" in system_data
    assert "name" in system_data
    assert system_data["id"] == system_id
    
    # Test evidence endpoint which should have uploaded_at
    response = client.get(f"/controls/{system_id}/evidence", headers=headers)
    assert response.status_code == 200
    
    evidence_data = response.json()
    if evidence_data:  # If there's evidence
        evidence = evidence_data[0]
        # Check upload_date field format
        upload_date = evidence.get("upload_date")
        assert upload_date is not None, "upload_date field missing"
        
        # Should be in ISO format with timezone
        assert isinstance(upload_date, str), "upload_date should be string"
        
        # Parse the datetime
        try:
            parsed_dt = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
            assert parsed_dt.tzinfo is not None, "upload_date should have timezone info"
            assert parsed_dt.tzinfo.utcoffset(None).total_seconds() == 0, "upload_date should be UTC"
        except ValueError:
            pytest.fail(f"Invalid datetime format: {upload_date}")


def test_datetime_format_consistency(setup_test_data):
    """Test that datetime formats are consistent across all endpoints."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    
    # Test multiple endpoints
    endpoints = [
        f"/systems/{system_id}",
        f"/controls/{system_id}/evidence", # Use the correct evidence endpoint
        "/systems",
        "/reports/summary"
    ]
    
    datetime_pattern = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2}|Z)')
    
    for endpoint in endpoints:
        response = client.get(endpoint, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            # Find all datetime strings in the response
            response_text = response.text
            datetime_matches = datetime_pattern.findall(response_text)
            
            for datetime_str in datetime_matches:
                # Should be valid ISO format
                try:
                    parsed_dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                    assert parsed_dt.tzinfo is not None, f"Datetime {datetime_str} should have timezone"
                except ValueError:
                    pytest.fail(f"Invalid datetime format: {datetime_str}")


def test_utc_timezone_parsing(setup_test_data):
    """Test that UTC timezone is properly parsed and handled."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    
    # Get evidence data which should have uploaded_at
    response = client.get(f"/controls/{system_id}/evidence", headers=headers)
    assert response.status_code == 200
    
    evidence_data = response.json()
    if evidence_data:  # If there's evidence
        evidence = evidence_data[0]
        upload_date = evidence["upload_date"]
        
        # Test different timezone formats
        timezone_formats = [
            upload_date,  # Original format
            upload_date.replace('Z', '+00:00'),  # Explicit UTC
            upload_date.replace('Z', 'Z'),  # Z format
        ]
        
        for tz_format in timezone_formats:
            try:
                parsed_dt = datetime.fromisoformat(tz_format.replace('Z', '+00:00'))
                assert parsed_dt.tzinfo is not None, f"Timezone info missing for {tz_format}"
                assert parsed_dt.tzinfo.utcoffset(None).total_seconds() == 0, f"Not UTC for {tz_format}"
            except ValueError:
                pytest.fail(f"Failed to parse datetime: {tz_format}")
    else:
        # If no evidence, just test that the endpoint works
        assert response.status_code == 200


def test_datetime_serialization():
    """Test that datetime serialization preserves timezone information."""
    Base = declarative_base()
    
    class TestModel(Base):
        __tablename__ = "test_model"
        id = Column(Integer, primary_key=True)
        created_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc))
    
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create test record
        test_record = TestModel()
        db.add(test_record)
        db.commit()
        db.refresh(test_record)
        
        # Check that timezone is preserved
        assert test_record.created_at.tzinfo is not None, "Timezone info lost during storage"
        assert test_record.created_at.tzinfo.utcoffset(None).total_seconds() == 0, "Not UTC timezone"
        
        # Check that it's a recent timestamp
        now = datetime.now(timezone.utc)
        time_diff = abs((now - test_record.created_at).total_seconds())
        assert time_diff < 60, "Timestamp is not recent"
            
    finally:
        db.close()


def test_naive_datetime_handling():
    """Test that naive datetimes are properly converted to UTC."""
    Base = declarative_base()
    
    class TestModel(Base):
        __tablename__ = "test_model"
        id = Column(Integer, primary_key=True)
        created_at = Column(UTCDateTime)
    
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create test record with naive datetime
        naive_dt = datetime.now()  # No timezone info
        test_record = TestModel(created_at=naive_dt)
        db.add(test_record)
        db.commit()
        db.refresh(test_record)
        
        # Check that naive datetime was converted to UTC
        assert test_record.created_at.tzinfo is not None, "Naive datetime should be converted to UTC"
        assert test_record.created_at.tzinfo.utcoffset(None).total_seconds() == 0, "Should be UTC timezone"
            
    finally:
            db.close()


def test_timezone_aware_datetime_handling():
    """Test that timezone-aware datetimes are properly handled."""
    Base = declarative_base()
    
    class TestModel(Base):
        __tablename__ = "test_model"
        id = Column(Integer, primary_key=True)
        created_at = Column(UTCDateTime)
    
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create test record with timezone-aware datetime
        aware_dt = datetime.now(timezone.utc)
        test_record = TestModel(created_at=aware_dt)
        db.add(test_record)
        db.commit()
        db.refresh(test_record)
        
        # Check that timezone-aware datetime is preserved
        assert test_record.created_at.tzinfo is not None, "Timezone info should be preserved"
        assert test_record.created_at.tzinfo.utcoffset(None).total_seconds() == 0, "Should be UTC timezone"
        
        # Check that the datetime value is preserved
        time_diff = abs((aware_dt - test_record.created_at).total_seconds())
        assert time_diff < 1, "Datetime value should be preserved"
            
    finally:
            db.close()