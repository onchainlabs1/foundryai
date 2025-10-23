"""
Test ZIP manifest generation and validation
"""

import json
import hashlib
import zipfile
from io import BytesIO
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Organization, AISystem, Control, Evidence
from app.api.routes.reports import _generate_annex_iv_zip


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
def test_system_for_zip(db_session):
    """Create system for ZIP testing."""
    org = Organization(
        name="ZIP Test Corp",
        api_key="zip-test-key",
        org_role="provider"
    )
    db_session.add(org)
    db_session.commit()
    
    system = create_test_system(
        org_id=org.id,
        name="ZIP Test System",
        purpose="Testing ZIP manifest generation",
        ai_act_class="minimal"
    )
    db_session.add(system)
    db_session.commit()
    
    # Add controls
    control = Control(
        org_id=org.id,
        system_id=system.id,
        iso_clause="A.5.1",
        name="Test Control",
        status="implemented",
        owner_email="test@zipcorp.com"
    )
    db_session.add(control)
    db_session.commit()
    
    # Add evidence
    evidence = Evidence(
        org_id=org.id,
        system_id=system.id,
        control_id=control.id,
        label="Test Evidence",
        file_path="/evidence/test.pdf",
        version="1.0",
        checksum="test_checksum_12345"
    )
    db_session.add(evidence)
    db_session.commit()
    
    return {"org": org, "system": system}


@pytest.mark.asyncio
async def test_zip_manifest_generation(db_session, test_system_for_zip):
    """Test that ZIP export includes manifest.json with correct hashes."""
    
    org = test_system_for_zip["org"]
    system = test_system_for_zip["system"]
    
    print("\n📦 ZIP MANIFEST TEST")
    print("=" * 60)
    
    # Generate ZIP
    response = await _generate_annex_iv_zip(system.id, org, db_session)
    
    # Extract ZIP content
    zip_content = b""
    async for chunk in response.body_iterator:
        zip_content += chunk
    
    # Open ZIP and read manifest
    with zipfile.ZipFile(BytesIO(zip_content), 'r') as zip_file:
        print(f"✅ ZIP contains {len(zip_file.namelist())} files")
        
        # Test 1: manifest.json exists
        assert "manifest.json" in zip_file.namelist()
        print("✅ TEST 1 PASSED: manifest.json exists in ZIP")
        
        # Test 2: Read and parse manifest
        manifest_content = zip_file.read("manifest.json").decode('utf-8')
        manifest = json.loads(manifest_content)
        print("✅ TEST 2 PASSED: manifest.json is valid JSON")
        
        # Test 3: Manifest schema validation
        assert "system_id" in manifest
        assert "generated_at" in manifest
        assert "generator_version" in manifest
        assert "artifacts" in manifest
        assert "sources" in manifest
        print("✅ TEST 3 PASSED: Manifest has required fields")
        
        # Test 4: System ID matches
        assert manifest["system_id"] == system.id
        print(f"✅ TEST 4 PASSED: System ID = {manifest['system_id']}")
        
        # Test 5: Artifacts list not empty
        assert len(manifest["artifacts"]) > 0
        print(f"✅ TEST 5 PASSED: {len(manifest['artifacts'])} artifacts in manifest")
        
        # Test 6: Each artifact has required fields
        for artifact in manifest["artifacts"]:
            assert "name" in artifact
            assert "sha256" in artifact
            assert "bytes" in artifact
        print("✅ TEST 6 PASSED: All artifacts have name, sha256, bytes")
        
        # Test 7: Verify hash matches actual file content
        first_artifact = None
        for artifact in manifest["artifacts"]:
            if artifact["name"] != "manifest.json":  # Skip manifest itself
                first_artifact = artifact
                break
        
        if first_artifact:
            actual_content = zip_file.read(first_artifact["name"])
            actual_hash = hashlib.sha256(actual_content).hexdigest()
            assert first_artifact["sha256"] == actual_hash
            print(f"✅ TEST 7 PASSED: Hash verified for {first_artifact['name']}")
        
        # Test 8: Verify byte sizes match
        if first_artifact:
            actual_size = len(actual_content)
            assert first_artifact["bytes"] == actual_size
            print(f"✅ TEST 8 PASSED: Size verified ({actual_size} bytes)")
        
        # Test 9: Generator version present
        assert manifest["generator_version"] == "1.0.0"
        print(f"✅ TEST 9 PASSED: Generator version = {manifest['generator_version']}")
        
        # Test 10: Timestamp is ISO format
        from datetime import datetime
from tests.conftest import create_test_system
        datetime.fromisoformat(manifest["generated_at"])  # Will raise if invalid
        print(f"✅ TEST 10 PASSED: Timestamp is valid ISO format")
    
    print("\n" + "=" * 60)
    print("🎉 ALL ZIP MANIFEST TESTS PASSED!")
    print("=" * 60)
    
    # Print manifest preview
    print("\n📄 Manifest Preview:")
    print("-" * 60)
    print(json.dumps(manifest, indent=2)[:800])
    print("-" * 60)
