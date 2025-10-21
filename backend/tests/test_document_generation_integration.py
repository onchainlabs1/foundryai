"""
Integration test for document generation with real data
"""

import pytest
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
def test_org(db_session):
    """Create test organization."""
    org = Organization(
        name="Test Compliance Co",
        api_key="test-key",
        primary_contact_name="Jane Smith",
        primary_contact_email="jane@testco.com",
        dpo_contact_name="John DPO",
        dpo_contact_email="dpo@testco.com",
        org_role="provider"
    )
    db_session.add(org)
    db_session.commit()
    return org


@pytest.fixture
def complete_system(db_session, test_org):
    """Create a complete test system with all data."""
    system = AISystem(
        org_id=test_org.id,
        name="Risk Assessment AI",
        purpose="Automated risk scoring for financial applications",
        domain="Finance",
        owner_email="owner@testco.com",
        deployment_context="Production system",
        lifecycle_stage="Production",
        affected_users="Financial analysts and customers",
        third_party_providers="AWS, OpenAI API",
        risk_category="High",
        ai_act_class="high-risk",
        impacts_fundamental_rights=True,
        uses_biometrics=False,
        uses_gpai=True,
        personal_data_processed=True
    )
    db_session.add(system)
    db_session.commit()
    
    # Add risks
    risks = [
        AIRisk(
            org_id=test_org.id,
            system_id=system.id,
            description="Algorithmic bias in credit scoring",
            likelihood="M",
            impact="H",
            mitigation="Regular fairness audits and bias testing",
            residual_risk="Low",
            owner_email="risk@testco.com",
            priority="high"
        ),
        AIRisk(
            org_id=test_org.id,
            system_id=system.id,
            description="Data privacy breach",
            likelihood="L",
            impact="H",
            mitigation="Encryption, access controls, monitoring",
            residual_risk="Medium",
            owner_email="security@testco.com",
            priority="high"
        ),
        AIRisk(
            org_id=test_org.id,
            system_id=system.id,
            description="Model drift affecting accuracy",
            likelihood="M",
            impact="M",
            mitigation="Continuous monitoring and retraining",
            residual_risk="Low",
            owner_email="ml@testco.com",
            priority="medium"
        )
    ]
    for risk in risks:
        db_session.add(risk)
    
    # Add controls
    controls = [
        Control(
            org_id=test_org.id,
            system_id=system.id,
            iso_clause="A.5.1",
            name="Information security policies",
            priority="high",
            status="implemented",
            owner_email="ciso@testco.com",
            rationale="Corporate security policy approved by board"
        ),
        Control(
            org_id=test_org.id,
            system_id=system.id,
            iso_clause="A.6.1",
            name="Risk management process",
            priority="high",
            status="implemented",
            owner_email="risk@testco.com",
            rationale="ISO 31000 aligned risk management framework"
        )
    ]
    for control in controls:
        db_session.add(control)
    
    # Add oversight
    oversight = Oversight(
        org_id=test_org.id,
        system_id=system.id,
        oversight_mode="in_the_loop",
        intervention_rules="Human review required for scores below 0.5",
        manual_override=True,
        appeals_channel="appeals@testco.com",
        appeals_sla_days=5,
        appeals_responsible_email="support@testco.com",
        ethics_committee=True,
        training_plan="Quarterly AI ethics training for all staff",
        comm_plan="Monthly transparency reports to stakeholders",
        external_disclosure=True
    )
    db_session.add(oversight)
    
    # Add PMM
    pmm = PMM(
        org_id=test_org.id,
        system_id=system.id,
        logging_scope="All prediction inputs, outputs, and confidence scores",
        retention_months=24,
        drift_threshold="5%",
        fairness_metrics="Accuracy, precision, recall, F1-score, demographic parity",
        incident_tool="Jira",
        audit_frequency="quarterly",
        management_review_frequency="semiannual",
        improvement_plan="Continuous improvement based on monitoring data",
        eu_db_required=True,
        eu_db_status="pending"
    )
    db_session.add(pmm)
    
    db_session.commit()
    return system


def test_document_generation_with_real_data(db_session, test_org, complete_system):
    """Test that document generation uses real data, not placeholders."""
    
    generator = DocumentGenerator()
    
    # Mock onboarding data (for backwards compatibility)
    onboarding_data = {}
    
    # Generate documents
    result = generator.generate_all_documents(
        system_id=complete_system.id,
        org_id=test_org.id,
        onboarding_data=onboarding_data,
        db=db_session
    )
    
    # Verify documents were generated
    assert len(result) > 0
    assert "risk_assessment" in result
    assert result["risk_assessment"]["markdown_available"] == True
    
    # Read the generated risk assessment
    from pathlib import Path
    output_dir = Path(__file__).parent.parent / "generated_documents"
    risk_assessment_path = output_dir / f"org_{test_org.id}" / f"system_{complete_system.id}" / "risk_assessment.md"
    
    assert risk_assessment_path.exists(), f"Risk assessment file not found at {risk_assessment_path}"
    
    content = risk_assessment_path.read_text()
    
    # Verify NO placeholders
    assert "[System Name]" not in content
    assert "TBD" not in content
    assert "PLACEHOLDER" not in content.upper()
    
    # Verify REAL data appears
    assert "Risk Assessment AI" in content  # System name
    assert "Test Compliance Co" in content  # Company name
    assert "Algorithmic bias in credit scoring" in content  # Real risk
    assert "Data privacy breach" in content  # Another real risk
    assert "Model drift affecting accuracy" in content  # Third risk
    
    print("✅ Document generation test PASSED - Real data is being used!")
    print(f"📄 Generated document preview (first 500 chars):")
    print(content[:500])


def test_soa_generation_with_controls(db_session, test_org, complete_system):
    """Test that SoA includes real controls data."""
    
    generator = DocumentGenerator()
    onboarding_data = {}
    
    # Generate documents
    result = generator.generate_all_documents(
        system_id=complete_system.id,
        org_id=test_org.id,
        onboarding_data=onboarding_data,
        db=db_session
    )
    
    # Read the generated SoA
    from pathlib import Path
    output_dir = Path(__file__).parent.parent / "generated_documents"
    soa_path = output_dir / f"org_{test_org.id}" / f"system_{complete_system.id}" / "soa.md"
    
    assert soa_path.exists(), f"SoA file not found at {soa_path}"
    
    content = soa_path.read_text()
    
    # Verify real controls appear
    assert "A.5.1" in content  # ISO clause
    assert "Information security policies" in content  # Control name
    assert "ciso@testco.com" in content  # Owner email
    assert "implemented" in content.lower()  # Status
    
    print("✅ SoA generation test PASSED - Real controls are included!")


def test_pmm_generation_with_monitoring_data(db_session, test_org, complete_system):
    """Test that PMM includes real monitoring configuration."""
    
    generator = DocumentGenerator()
    onboarding_data = {}
    
    # Generate documents
    result = generator.generate_all_documents(
        system_id=complete_system.id,
        org_id=test_org.id,
        onboarding_data=onboarding_data,
        db=db_session
    )
    
    # Read the generated PMM report
    from pathlib import Path
    output_dir = Path(__file__).parent.parent / "generated_documents"
    pmm_path = output_dir / f"org_{test_org.id}" / f"system_{complete_system.id}" / "monitoring_report.md"
    
    assert pmm_path.exists(), f"PMM file not found at {pmm_path}"
    
    content = pmm_path.read_text()
    
    # Verify real PMM data appears
    assert "All prediction inputs, outputs, and confidence scores" in content  # Logging scope
    assert "24 months" in content or "24" in content  # Retention
    assert "5%" in content  # Drift threshold
    assert "quarterly" in content.lower()  # Audit frequency
    
    print("✅ PMM generation test PASSED - Real monitoring data is included!")
