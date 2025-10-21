"""
Test GPAI Transparency Notice conditional generation
"""

import pytest
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Organization, AISystem, AIRisk, Oversight, PMM
from app.services.document_generator import DocumentGenerator


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


def test_gpai_system_generates_transparency_notice(db_session):
    """Test that GPAI systems generate transparency notice."""
    
    org = Organization(
        name="GPAI Test Corp",
        api_key="gpai-key",
        primary_contact_name="Alice Manager",
        primary_contact_email="alice@gpaitest.com",
        dpo_contact_name="Bob DPO",
        dpo_contact_email="dpo@gpaitest.com",
        org_role="provider"
    )
    db_session.add(org)
    db_session.commit()
    
    # System WITH uses_gpai=True
    gpai_system = AISystem(
        org_id=org.id,
        name="GPAI Content Generator",
        purpose="AI-powered content generation using large language models",
        domain="Content Creation",
        uses_gpai=True,
        is_general_purpose_ai=True,
        personal_data_processed=True,
        ai_act_class="limited"
    )
    db_session.add(gpai_system)
    db_session.commit()
    
    # Add minimal oversight and PMM
    oversight = Oversight(
        org_id=org.id,
        system_id=gpai_system.id,
        oversight_mode="on_the_loop",
        intervention_rules="Human review for sensitive content",
        manual_override=True,
        appeals_channel="support@gpaitest.com",
        appeals_sla_days=3,
        appeals_responsible_email="compliance@gpaitest.com"
    )
    db_session.add(oversight)
    
    pmm = PMM(
        org_id=org.id,
        system_id=gpai_system.id,
        logging_scope="All generated content and user prompts",
        retention_months=12,
        drift_threshold="10%",
        fairness_metrics="Content quality, accuracy, appropriateness",
        audit_frequency="monthly",
        management_review_frequency="quarterly",
        improvement_plan="User feedback integration"
    )
    db_session.add(pmm)
    db_session.commit()
    
    # Generate documents
    generator = DocumentGenerator()
    result = generator.generate_all_documents(
        system_id=gpai_system.id,
        org_id=org.id,
        onboarding_data={},
        db=db_session
    )
    
    print("\n🤖 GPAI TRANSPARENCY NOTICE TEST")
    print("=" * 60)
    
    # Test 1: Transparency notice was generated
    assert "transparency_notice_gpai" in result
    print("✅ TEST 1 PASSED: Transparency notice generated for GPAI system")
    
    # Test 2: File exists
    output_dir = Path(__file__).parent.parent / "generated_documents"
    notice_path = output_dir / f"org_{org.id}" / f"system_{gpai_system.id}" / "transparency_notice_gpai.md"
    assert notice_path.exists()
    print("✅ TEST 2 PASSED: Transparency notice file exists")
    
    # Test 3: Content is correct
    content = notice_path.read_text()
    assert "# Transparency Notice - General Purpose AI" in content
    assert "GPAI Content Generator" in content
    assert "General Purpose AI" in content
    print("✅ TEST 3 PASSED: Transparency notice content correct")
    
    # Test 4: Required sections present
    assert "## 2. User Notification" in content
    assert "## 3. AI Output Labeling" in content
    assert "## 8. Appeals and Complaints" in content
    print("✅ TEST 4 PASSED: Required sections present")
    
    # Test 5: Real data from system
    assert "AI-powered content generation" in content
    assert "support@gpaitest.com" in content
    assert "3" in content  # Appeals SLA days
    print("✅ TEST 5 PASSED: Real system data in transparency notice")
    
    print("\n" + "=" * 60)
    print("🎉 ALL GPAI TRANSPARENCY TESTS PASSED!")
    print("=" * 60)


def test_non_gpai_system_no_transparency_notice(db_session):
    """Test that non-GPAI systems do NOT generate transparency notice."""
    
    org = Organization(
        name="NonGPAI Test Corp",
        api_key="nongpai-key",
        primary_contact_name="Charlie Manager",
        primary_contact_email="charlie@nongpai.com",
        org_role="deployer"
    )
    db_session.add(org)
    db_session.commit()
    
    # System WITHOUT uses_gpai
    non_gpai_system = AISystem(
        org_id=org.id,
        name="Simple Rule-Based System",
        purpose="Rule-based decision system",
        domain="Operations",
        uses_gpai=False,
        is_general_purpose_ai=False,
        ai_act_class="minimal"
    )
    db_session.add(non_gpai_system)
    db_session.commit()
    
    # Generate documents
    generator = DocumentGenerator()
    result = generator.generate_all_documents(
        system_id=non_gpai_system.id,
        org_id=org.id,
        onboarding_data={},
        db=db_session
    )
    
    print("\n🚫 NON-GPAI SYSTEM TEST")
    print("=" * 60)
    
    # Test: Transparency notice should NOT be in generated docs list
    assert "transparency_notice_gpai" not in result
    print("✅ TEST PASSED: Non-GPAI system does not generate transparency notice in result")
    
    # Verify file doesn't exist in system-specific directory
    output_dir = Path(__file__).parent.parent / "generated_documents"
    system_dir = output_dir / f"org_{org.id}" / f"system_{non_gpai_system.id}"
    
    if system_dir.exists():
        notice_path = system_dir / "transparency_notice_gpai.md"
        assert not notice_path.exists(), f"Transparency notice should not exist for non-GPAI system"
        print("✅ TEST PASSED: Transparency notice file not created for this system")
    else:
        print("✅ TEST PASSED: System directory is clean (no documents yet)")
    
    print("\n" + "=" * 60)
    print("🎉 NON-GPAI CONDITIONAL LOGIC WORKS!")
    print("=" * 60)
