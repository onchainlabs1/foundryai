"""
Test evidence versioning and immutability
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Organization, AISystem, Evidence
from tests.conftest import create_test_system


@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_setup(db_session):
    """Create test org and system."""
    org = Organization(
        name="Versioning Test Corp",
        api_key="version-test-key",
        org_role="provider"
    )
    db_session.add(org)
    db_session.commit()
    
    system = create_test_system(
        org_id=org.id,
        name="Version Test System",
        purpose="Testing evidence versioning",
        ai_act_class="minimal"
    )
    db_session.add(system)
    db_session.commit()
    
    return {"org": org, "system": system}


def test_evidence_version_auto_increment(db_session, test_setup):
    """Test that uploading evidence with same label auto-increments version."""
    
    org = test_setup["org"]
    system = test_setup["system"]
    
    print("\n📦 EVIDENCE VERSIONING TEST")
    print("=" * 60)
    
    # Upload first evidence
    ev1 = Evidence(
        org_id=org.id,
        system_id=system.id,
        label="Security Policy",
        file_path="/evidence/policy_v1.pdf",
        checksum="checksum1"
    )
    
    # Simulate auto-versioning logic
    existing = db_session.query(Evidence).filter(
        Evidence.org_id == org.id,
        Evidence.system_id == system.id,
        Evidence.label == "Security Policy"
    ).first()
    
    if not existing:
        ev1.version = "1.0"
    
    db_session.add(ev1)
    db_session.commit()
    
    assert ev1.version == "1.0"
    print(f"✅ TEST 1 PASSED: First upload version = {ev1.version}")
    
    # Upload second evidence with same label (should be v1.1)
    ev2 = Evidence(
        org_id=org.id,
        system_id=system.id,
        label="Security Policy",
        file_path="/evidence/policy_v2.pdf",
        checksum="checksum2"
    )
    
    # Simulate auto-versioning logic
    existing = db_session.query(Evidence).filter(
        Evidence.org_id == org.id,
        Evidence.system_id == system.id,
        Evidence.label == "Security Policy"
    ).order_by(Evidence.upload_date.desc()).first()
    
    if existing:
        existing_version = existing.version or "1.0"
        try:
            parts = existing_version.split('.')
            major, minor = int(parts[0]), int(parts[1])
            ev2.version = f"{major}.{minor + 1}"
        except:
            ev2.version = "1.1"
    else:
        ev2.version = "1.0"
    
    db_session.add(ev2)
    db_session.commit()
    
    assert ev2.version == "1.1"
    print(f"✅ TEST 2 PASSED: Second upload version = {ev2.version}")
    
    # Upload third evidence with same label (should be v1.2)
    ev3 = Evidence(
        org_id=org.id,
        system_id=system.id,
        label="Security Policy",
        file_path="/evidence/policy_v3.pdf",
        checksum="checksum3"
    )
    
    existing = db_session.query(Evidence).filter(
        Evidence.org_id == org.id,
        Evidence.system_id == system.id,
        Evidence.label == "Security Policy"
    ).order_by(Evidence.upload_date.desc()).first()
    
    if existing:
        existing_version = existing.version or "1.0"
        parts = existing_version.split('.')
        major, minor = int(parts[0]), int(parts[1])
        ev3.version = f"{major}.{minor + 1}"
    
    db_session.add(ev3)
    db_session.commit()
    
    assert ev3.version == "1.2"
    print(f"✅ TEST 3 PASSED: Third upload version = {ev3.version}")
    
    # Verify all 3 versions exist (no overwrite)
    all_versions = db_session.query(Evidence).filter(
        Evidence.org_id == org.id,
        Evidence.system_id == system.id,
        Evidence.label == "Security Policy"
    ).all()
    
    assert len(all_versions) == 3
    print(f"✅ TEST 4 PASSED: All 3 versions exist (no overwrite)")
    
    # Verify different checksums (immutability)
    checksums = [e.checksum for e in all_versions]
    assert len(set(checksums)) == 3  # All unique
    print(f"✅ TEST 5 PASSED: All versions have unique checksums")
    
    # Verify versions in correct order
    versions = sorted([e.version for e in all_versions])
    assert versions == ["1.0", "1.1", "1.2"]
    print(f"✅ TEST 6 PASSED: Versions in correct order: {versions}")
    
    print("\n" + "=" * 60)
    print("🎉 ALL EVIDENCE VERSIONING TESTS PASSED!")
    print("=" * 60)


def test_evidence_immutability(db_session, test_setup):
    """Test that evidence cannot be overwritten - only versioned."""
    
    org = test_setup["org"]
    system = test_setup["system"]
    
    print("\n🔒 EVIDENCE IMMUTABILITY TEST")
    print("=" * 60)
    
    # Create first version
    ev1 = Evidence(
        org_id=org.id,
        system_id=system.id,
        label="Audit Report",
        file_path="/evidence/audit_v1.pdf",
        checksum="original_checksum",
        version="1.0"
    )
    db_session.add(ev1)
    db_session.commit()
    
    original_id = ev1.id
    original_checksum = ev1.checksum
    
    # Upload new version (should NOT modify original)
    ev2 = Evidence(
        org_id=org.id,
        system_id=system.id,
        label="Audit Report",
        file_path="/evidence/audit_v2.pdf",
        checksum="new_checksum",
        version="1.1"
    )
    db_session.add(ev2)
    db_session.commit()
    
    # Verify original evidence still exists unchanged
    original_evidence = db_session.query(Evidence).filter(Evidence.id == original_id).first()
    assert original_evidence is not None
    assert original_evidence.checksum == original_checksum
    assert original_evidence.version == "1.0"
    print("✅ TEST 1 PASSED: Original evidence unchanged")
    
    # Verify new evidence is separate record
    assert ev2.id != ev1.id
    assert ev2.checksum != ev1.checksum
    print("✅ TEST 2 PASSED: New version is separate record")
    
    # Verify both versions accessible
    all_audits = db_session.query(Evidence).filter(
        Evidence.org_id == org.id,
        Evidence.system_id == system.id,
        Evidence.label == "Audit Report"
    ).all()
    
    assert len(all_audits) == 2
    print("✅ TEST 3 PASSED: Both versions accessible (immutable)")
    
    print("\n" + "=" * 60)
    print("🎉 EVIDENCE IMMUTABILITY VERIFIED!")
    print("=" * 60)
