"""
Test Annex IV generation with complete data
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Organization, AISystem, AIRisk, Control, Oversight, PMM, Evidence
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


@pytest.fixture
def complete_system_with_evidence(db_session):
    """Create a complete test system with evidence."""
    org = Organization(
        name="Audit Test Corp",
        api_key="audit-key",
        primary_contact_name="Chief Compliance Officer",
        primary_contact_email="cco@auditcorp.com",
        dpo_contact_name="Data Protection Officer",
        dpo_contact_email="dpo@auditcorp.com",
        org_role="provider"
    )
    db_session.add(org)
    db_session.commit()
    
    system = AISystem(
        org_id=org.id,
        name="Credit Scoring System",
        purpose="Automated creditworthiness assessment for loan applications",
        domain="Finance",
        owner_email="ml-lead@auditcorp.com",
        deployment_context="Production - Customer-facing",
        lifecycle_stage="Production",
        affected_users="Loan applicants and financial analysts",
        third_party_providers="AWS, TransUnion credit data",
        risk_category="High",
        ai_act_class="high-risk",
        impacts_fundamental_rights=True,
        uses_biometrics=False,
        uses_gpai=False,
        personal_data_processed=True,
        system_role="provider",
        eu_db_status="registered"
    )
    db_session.add(system)
    db_session.commit()
    
    # Add risks
    risks = [
        AIRisk(
            org_id=org.id,
            system_id=system.id,
            description="Discriminatory bias in credit decisions based on protected characteristics",
            likelihood="M",
            impact="H",
            mitigation="Regular fairness audits, bias testing, demographic parity monitoring",
            residual_risk="Low",
            owner_email="risk@auditcorp.com",
            priority="high"
        ),
        AIRisk(
            org_id=org.id,
            system_id=system.id,
            description="Unauthorized access to personal financial data",
            likelihood="L",
            impact="H",
            mitigation="End-to-end encryption, role-based access controls, SOC 2 compliance",
            residual_risk="Low",
            owner_email="security@auditcorp.com",
            priority="high"
        ),
        AIRisk(
            org_id=org.id,
            system_id=system.id,
            description="Model performance degradation due to market changes",
            likelihood="M",
            impact="M",
            mitigation="Monthly model retraining, performance monitoring, A/B testing",
            residual_risk="Medium",
            owner_email="ml-ops@auditcorp.com",
            priority="medium"
        )
    ]
    for risk in risks:
        db_session.add(risk)
    
    # Add controls
    controls = [
        Control(
            org_id=org.id,
            system_id=system.id,
            iso_clause="A.5.1",
            name="Information security policies and procedures",
            priority="high",
            status="implemented",
            owner_email="ciso@auditcorp.com",
            rationale="Corporate ISMS certified to ISO 27001"
        ),
        Control(
            org_id=org.id,
            system_id=system.id,
            iso_clause="A.6.1",
            name="AI risk management framework",
            priority="high",
            status="implemented",
            owner_email="risk@auditcorp.com",
            rationale="ISO 31000-aligned risk management for AI systems"
        ),
        Control(
            org_id=org.id,
            system_id=system.id,
            iso_clause="A.8.1",
            name="Data classification and handling",
            priority="high",
            status="partial",
            owner_email="data-gov@auditcorp.com",
            rationale="Data governance framework in progress"
        )
    ]
    for control in controls:
        db_session.add(control)
    db_session.commit()
    
    # Add evidence
    evidence_items = [
        Evidence(
            org_id=org.id,
            system_id=system.id,
            control_id=controls[0].id,
            label="ISO 27001 Certificate",
            file_path="/evidence/iso27001_cert.pdf",
            version="1.0",
            checksum="abc123def456789",
            iso42001_clause="A.5.1"
        ),
        Evidence(
            org_id=org.id,
            system_id=system.id,
            control_id=controls[1].id,
            label="AI Risk Assessment Report Q4 2024",
            file_path="/evidence/risk_assessment_q4_2024.pdf",
            version="2.1",
            checksum="def456ghi789abc",
            iso42001_clause="A.6.1"
        )
    ]
    for ev in evidence_items:
        db_session.add(ev)
    
    # Add oversight
    oversight = Oversight(
        org_id=org.id,
        system_id=system.id,
        oversight_mode="in_the_loop",
        intervention_rules="Human review mandatory for credit scores < 600 and > 850",
        manual_override=True,
        appeals_channel="appeals@auditcorp.com",
        appeals_sla_days=3,
        appeals_responsible_email="compliance@auditcorp.com",
        ethics_committee=True,
        training_plan="Quarterly AI ethics and fairness training for all decision-makers",
        comm_plan="Monthly transparency reports to stakeholders and regulators",
        external_disclosure=True
    )
    db_session.add(oversight)
    
    # Add PMM
    pmm = PMM(
        org_id=org.id,
        system_id=system.id,
        logging_scope="All credit decisions, input features, scores, timestamps, reviewer overrides",
        retention_months=60,
        drift_threshold="3%",
        fairness_metrics="Demographic parity, equal opportunity, precision parity across protected groups",
        incident_tool="ServiceNow",
        audit_frequency="quarterly",
        management_review_frequency="semiannual",
        improvement_plan="Continuous model improvement based on fairness metrics and customer feedback",
        eu_db_required=True,
        eu_db_status="registered"
    )
    db_session.add(pmm)
    
    db_session.commit()
    return {"org": org, "system": system}


def test_annex_iv_generation_complete(db_session, complete_system_with_evidence):
    """Test that Annex IV is generated with all required sections."""
    
    org = complete_system_with_evidence["org"]
    system = complete_system_with_evidence["system"]
    
    generator = DocumentGenerator()
    result = generator.generate_all_documents(
        system_id=system.id,
        org_id=org.id,
        onboarding_data={},
        db=db_session
    )
    
    # Verify Annex IV was generated
    assert "annex_iv" in result
    assert result["annex_iv"]["markdown_available"] == True
    
    # Read the generated Annex IV
    output_dir = Path(__file__).parent.parent / "generated_documents"
    annex_iv_path = output_dir / f"org_{org.id}" / f"system_{system.id}" / "annex_iv.md"
    
    assert annex_iv_path.exists(), f"Annex IV file not found at {annex_iv_path}"
    
    content = annex_iv_path.read_text()
    
    print("\n📄 ANNEX IV GENERATION TEST")
    print("=" * 60)
    
    # Test 1: NO PLACEHOLDERS
    placeholders = ["[System Name]", "TBD", "PLACEHOLDER", "TODO", "N/A"]
    found_placeholders = [p for p in placeholders if p in content]
    
    assert len(found_placeholders) == 0, f"❌ Found placeholders: {found_placeholders}"
    print("✅ TEST 1 PASSED: No placeholders found")
    
    # Test 2: REAL SYSTEM DATA
    assert "Credit Scoring System" in content
    assert "Audit Test Corp" in content
    assert "Finance" in content
    assert "high-risk" in content
    print("✅ TEST 2 PASSED: Real system data present")
    
    # Test 3: RISKS SECTION
    assert "Discriminatory bias" in content
    assert "Unauthorized access to personal financial data" in content
    assert "Model performance degradation" in content
    print("✅ TEST 3 PASSED: All 3 risks present")
    
    # Test 4: CONTROLS SECTION
    assert "A.5.1" in content
    assert "A.6.1" in content
    assert "A.8.1" in content
    assert "Information security policies" in content
    print("✅ TEST 4 PASSED: All controls present")
    
    # Test 5: HUMAN OVERSIGHT SECTION
    assert "in_the_loop" in content
    assert "Human review mandatory" in content or "mandatory for credit scores" in content
    assert "appeals@auditcorp.com" in content
    print("✅ TEST 5 PASSED: Human oversight data present")
    
    # Test 6: PMM SECTION
    assert "60 months" in content or "60" in content
    assert "3%" in content
    assert "quarterly" in content.lower()
    print("✅ TEST 6 PASSED: PMM monitoring data present")
    
    # Test 7: EVIDENCE CITATIONS
    assert "Evidence Register" in content or "Evidence" in content
    assert "ISO 27001 Certificate" in content
    assert "abc123def456" in content  # Checksum truncated
    print("✅ TEST 7 PASSED: Evidence citations present")
    
    # Test 8: EU DATABASE STATUS
    assert "registered" in content.lower()
    assert "EU Database" in content or "EU DB" in content
    print("✅ TEST 8 PASSED: EU Database status present")
    
    # Test 9: ORGANIZATION INFO
    assert "Chief Compliance Officer" in content or "cco@auditcorp.com" in content
    assert "Data Protection Officer" in content or "dpo@auditcorp.com" in content
    print("✅ TEST 9 PASSED: Organization contacts present")
    
    # Test 10: DOCUMENT STRUCTURE
    assert "# Annex IV" in content
    assert "## 1. General Information" in content
    assert "## 3. Risk Assessment" in content
    assert "## 4. Controls and Measures" in content
    assert "## 5. Human Oversight" in content
    assert "## 6. Post-Market Monitoring" in content
    print("✅ TEST 10 PASSED: Document structure complete")
    
    print("\n" + "=" * 60)
    print("🎉 ALL 10 ANNEX IV TESTS PASSED!")
    print("=" * 60)
    
    # Print preview
    print("\n📄 ANNEX IV Preview (first 800 chars):")
    print("-" * 60)
    print(content[:800])
    print("-" * 60)
    
    return True
