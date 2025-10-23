"""
Test Instructions for Use generation
"""

import pytest
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Organization, AISystem, AIRisk, Oversight, PMM
from app.services.document_generator import DocumentGenerator
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
def high_risk_system_complete(db_session):
    """Create high-risk system with full instructions data."""
    org = Organization(
        name="FinTech Solutions Ltd",
        api_key="fintech-key",
        primary_contact_name="Sarah Johnson",
        primary_contact_email="sarah@fintech.com",
        dpo_contact_name="Michael DPO",
        dpo_contact_email="dpo@fintech.com",
        org_role="provider"
    )
    db_session.add(org)
    db_session.commit()
    
    system = create_test_system(
        org_id=org.id,
        name="Loan Decisioning AI",
        purpose="Automated loan approval/rejection recommendations for consumer loans",
        domain="Finance",
        owner_email="ai-owner@fintech.com",
        deployment_context="Production - Customer-facing",
        lifecycle_stage="Production",
        affected_users="Loan applicants, underwriters, compliance team",
        ai_act_class="high-risk",
        impacts_fundamental_rights=True,
        personal_data_processed=True,
        uses_gpai=True,
        eu_db_status="registered"
    )
    db_session.add(system)
    db_session.commit()
    
    # Add risks with medium/high residual risk
    risks = [
        AIRisk(
            org_id=org.id,
            system_id=system.id,
            description="Algorithmic bias against protected demographics",
            likelihood="M",
            impact="H",
            mitigation="Regular fairness testing and bias mitigation",
            residual_risk="Medium",
            owner_email="compliance@fintech.com",
            priority="high"
        ),
        AIRisk(
            org_id=org.id,
            system_id=system.id,
            description="Incorrect loan decisions due to data quality issues",
            likelihood="M",
            impact="H",
            mitigation="Data validation and human review for edge cases",
            residual_risk="Medium",
            owner_email="quality@fintech.com",
            priority="high"
        )
    ]
    for risk in risks:
        db_session.add(risk)
    
    # Add oversight
    oversight = Oversight(
        org_id=org.id,
        system_id=system.id,
        oversight_mode="in_the_loop",
        intervention_rules="Human review required for all loan amounts > $50,000 and for applicants with marginal credit scores (600-650)",
        manual_override=True,
        appeals_channel="appeals@fintech.com",
        appeals_sla_days=5,
        appeals_responsible_email="compliance@fintech.com",
        ethics_committee=True,
        training_plan="Mandatory AI ethics and fairness training every 6 months for all decision-makers",
        comm_plan="Quarterly transparency reports to regulators and annual customer communication",
        external_disclosure=True
    )
    db_session.add(oversight)
    
    # Add PMM
    pmm = PMM(
        org_id=org.id,
        system_id=system.id,
        logging_scope="All loan decisions, applicant features, credit scores, AI recommendations, human overrides",
        retention_months=84,  # 7 years for financial records
        drift_threshold="2%",
        fairness_metrics="Equal opportunity, demographic parity, precision parity across gender and ethnicity",
        incident_tool="ServiceNow",
        audit_frequency="quarterly",
        management_review_frequency="semiannual",
        improvement_plan="Continuous model refinement based on fairness metrics and customer feedback",
        eu_db_required=True,
        eu_db_status="registered"
    )
    db_session.add(pmm)
    
    db_session.commit()
    return {"org": org, "system": system}


def test_instructions_for_use_generation(db_session, high_risk_system_complete):
    """Test Instructions for Use document generation."""
    
    org = high_risk_system_complete["org"]
    system = high_risk_system_complete["system"]
    
    generator = DocumentGenerator()
    result = generator.generate_all_documents(
        system_id=system.id,
        org_id=org.id,
        onboarding_data={},
        db=db_session
    )
    
    # Verify Instructions for Use was generated
    assert "instructions_for_use" in result
    assert result["instructions_for_use"]["markdown_available"] == True
    
    # Read the generated document
    output_dir = Path(__file__).parent.parent / "generated_documents"
    ifu_path = output_dir / f"org_{org.id}" / f"system_{system.id}" / "instructions_for_use.md"
    
    assert ifu_path.exists(), f"Instructions for Use not found at {ifu_path}"
    
    content = ifu_path.read_text()
    
    print("\n📖 INSTRUCTIONS FOR USE GENERATION TEST")
    print("=" * 60)
    
    # Test 1: Document title and structure
    assert "# Instructions for Use" in content
    assert "## 1. Intended Purpose" in content
    assert "## 2. User Responsibilities" in content
    assert "## 3. System Limitations" in content
    assert "## 4. Warnings and Precautions" in content
    print("✅ TEST 1 PASSED: Document structure complete")
    
    # Test 2: Real system purpose
    assert "Automated loan approval/rejection recommendations" in content
    assert "Finance" in content
    print("✅ TEST 2 PASSED: Real system purpose present")
    
    # Test 3: User responsibilities (accept both > and &gt; for HTML encoding)
    assert ("Human review required for all loan amounts > $50,000" in content or 
            "Human review required for all loan amounts &gt; $50,000" in content)
    assert "in_the_loop" in content
    print("✅ TEST 3 PASSED: User responsibilities present")
    
    # Test 4: System limitations from risks
    assert "Algorithmic bias against protected demographics" in content
    assert "Incorrect loan decisions due to data quality issues" in content
    print("✅ TEST 4 PASSED: System limitations from risks")
    
    # Test 5: High-risk warnings
    assert "HIGH-RISK AI SYSTEM WARNING" in content
    assert "EU AI Act" in content
    print("✅ TEST 5 PASSED: High-risk warnings present")
    
    # Test 6: Personal data warnings
    assert "PERSONAL DATA PROCESSING" in content
    assert "GDPR" in content
    assert "84 months" in content  # Retention
    print("✅ TEST 6 PASSED: Personal data warnings present")
    
    # Test 7: Fundamental rights warnings
    assert "FUNDAMENTAL RIGHTS IMPACT" in content
    assert "FRIA" in content
    print("✅ TEST 7 PASSED: Fundamental rights warnings present")
    
    # Test 8: GPAI warnings
    assert "GENERAL PURPOSE AI" in content
    print("✅ TEST 8 PASSED: GPAI warnings present")
    
    # Test 9: Appeals process
    assert "appeals@fintech.com" in content
    assert "5 days" in content
    print("✅ TEST 9 PASSED: Appeals process documented")
    
    # Test 10: Monitoring and logging
    assert "All loan decisions, applicant features" in content
    assert "84 months" in content
    assert "quarterly" in content.lower()
    print("✅ TEST 10 PASSED: Monitoring configuration present")
    
    # Test 11: Contact information
    assert "Sarah Johnson" in content
    assert "Michael DPO" in content
    assert "dpo@fintech.com" in content
    print("✅ TEST 11 PASSED: Contact information complete")
    
    # Test 12: No placeholders
    assert "TBD" not in content
    assert "[System Name]" not in content
    assert "PLACEHOLDER" not in content.upper()
    print("✅ TEST 12 PASSED: No placeholders found")
    
    print("\n" + "=" * 60)
    print("🎉 ALL 12 INSTRUCTIONS FOR USE TESTS PASSED!")
    print("=" * 60)
    
    # Print preview
    print("\n📄 Instructions for Use Preview (first 1000 chars):")
    print("-" * 60)
    print(content[:1000])
    print("-" * 60)
