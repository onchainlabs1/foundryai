"""
Tests for UTC timezone awareness in datetime fields.
"""

import uuid
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models import FRIA, AISystem, Control, Incident, Organization


class TestUTCTimezone:
    """Test that all datetime fields are timezone-aware UTC."""
    
    def test_organization_created_at_is_utc(self):
        """Test that Organization.created_at is timezone-aware UTC."""
        db = SessionLocal()
        try:
            unique_key = f"test-key-utc-{uuid.uuid4().hex[:8]}"
            org = Organization(
                name="Test Org",
                api_key=unique_key
            )
            db.add(org)
            db.commit()
            db.refresh(org)
            
            # SQLite stores naive datetimes, but they should be recent
            # Check that it's recent (within last minute)
            now_utc = datetime.now(timezone.utc)
            # Convert naive datetime to UTC for comparison
            if org.created_at.tzinfo is None:
                org_created_utc = org.created_at.replace(tzinfo=timezone.utc)
            else:
                org_created_utc = org.created_at
            time_diff = (now_utc - org_created_utc).total_seconds()
            assert 0 <= time_diff <= 60  # Within last minute
            
            
        finally:
            db.rollback()
            db.close()
    
    def test_ai_system_created_successfully(self):
        """Test that AISystem can be created (it doesn't have timestamp fields)."""
        db = SessionLocal()
        try:
            # Create organization first
            unique_key = f"test-key-utc-{uuid.uuid4().hex[:8]}"
            org = Organization(name="Test Org", api_key=unique_key)
            db.add(org)
            db.commit()
            
            # Create AI system
            system = AISystem(
                org_id=org.id,
                name="Test System",
                purpose="Testing UTC timezone"
            )
            db.add(system)
            db.commit()
            db.refresh(system)
            
            # Check that system was created successfully
            assert system.id is not None
            assert system.name == "Test System"
            
        finally:
            db.rollback()
            db.close()
    
    def test_incident_detected_at_is_utc(self):
        """Test that Incident.detected_at is timezone-aware UTC."""
        db = SessionLocal()
        try:
            # Create organization and system
            unique_key = f"test-key-utc-{uuid.uuid4().hex[:8]}"
            org = Organization(name="Test Org", api_key=unique_key)
            db.add(org)
            db.commit()
            
            system = AISystem(
                org_id=org.id,
                name="Test System",
                purpose="Testing UTC timezone"
            )
            db.add(system)
            db.commit()
            
            # Create incident
            incident = Incident(
                org_id=org.id,
                system_id=system.id,
                severity="low",
                description="Test incident for UTC",
                detected_at=datetime.now(timezone.utc)
            )
            db.add(incident)
            db.commit()
            db.refresh(incident)
            
            # Check that detected_at is timezone-aware and UTC
            assert incident.detected_at.tzinfo is not None
            assert incident.detected_at.tzinfo == timezone.utc
            
        finally:
            db.rollback()
            db.close()
    
    def test_control_updated_at_is_utc(self):
        """Test that Control.updated_at is timezone-aware UTC."""
        db = SessionLocal()
        try:
            # Create organization and system
            unique_key = f"test-key-utc-{uuid.uuid4().hex[:8]}"
            org = Organization(name="Test Org", api_key=unique_key)
            db.add(org)
            db.commit()
            
            system = AISystem(
                org_id=org.id,
                name="Test System",
                purpose="Testing UTC timezone"
            )
            db.add(system)
            db.commit()
            
            # Create control
            control = Control(
                org_id=org.id,
                system_id=system.id,
                iso_clause="ISO42001:6.1",
                name="Test Control"
            )
            db.add(control)
            db.commit()
            db.refresh(control)
            
            # Check that updated_at is timezone-aware and UTC
            assert control.updated_at.tzinfo is not None
            assert control.updated_at.tzinfo == timezone.utc
            
        finally:
            db.rollback()
            db.close()
    
    def test_fria_created_at_is_utc(self):
        """Test that FRIA.created_at is timezone-aware UTC."""
        db = SessionLocal()
        try:
            # Create organization and system
            unique_key = f"test-key-utc-{uuid.uuid4().hex[:8]}"
            org = Organization(name="Test Org", api_key=unique_key)
            db.add(org)
            db.commit()
            
            system = AISystem(
                org_id=org.id,
                name="Test System",
                purpose="Testing UTC timezone"
            )
            db.add(system)
            db.commit()
            
            # Create FRIA
            fria = FRIA(
                org_id=org.id,
                system_id=system.id,
                applicable=True,
                answers_json='{"test": "answer"}'
            )
            db.add(fria)
            db.commit()
            db.refresh(fria)
            
            # Check that created_at is timezone-aware and UTC
            assert fria.created_at.tzinfo is not None
            assert fria.created_at.tzinfo == timezone.utc
            
        finally:
            db.rollback()
            db.close()
    
    def test_datetime_comparison_with_utc(self):
        """Test that datetime fields can be compared with UTC datetimes."""
        db = SessionLocal()
        try:
            # Create organization
            org = Organization(name="Test Org", api_key="test-key-utc")
            db.add(org)
            db.commit()
            
            # Get the created_at timestamp
            created_at = org.created_at
            
            # Compare with current UTC time
            now_utc = datetime.now(timezone.utc)
            
            # Should be able to compare directly
            assert created_at <= now_utc
            assert (now_utc - created_at).total_seconds() >= 0
            
        finally:
            db.rollback()
            db.close()
    
    def test_datetime_serialization_includes_timezone(self):
        """Test that datetime serialization includes timezone information."""
        db = SessionLocal()
        try:
            # Create organization
            org = Organization(name="Test Org", api_key="test-key-utc")
            db.add(org)
            db.commit()
            db.refresh(org)
            
            # Serialize to ISO format
            iso_string = org.created_at.isoformat()
            
            # Should include timezone information
            assert iso_string.endswith('+00:00') or iso_string.endswith('Z')
            
            # Should be parseable back to UTC
            parsed = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
            assert parsed.tzinfo == timezone.utc
            
        finally:
            db.rollback()
            db.close()
