"""
Unit tests for Document Context Service
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Organization, AISystem, AIRisk, Control, Oversight, PMM, Evidence, FRIA
from app.services.document_context import DocumentContextService
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
def test_org(db_session):
    """Create test organization."""
    org = Organization(
        name="Test Company",
        api_key="test-key",
        primary_contact_name="John Doe",
        primary_contact_email="john@test.com",
        dpo_contact_name="Jane DPO",
        dpo_contact_email="dpo@test.com",
        org_role="provider"
    )
    db_session.add(org)
    db_session.commit()
    return org


@pytest.fixture
def test_system(db_session, test_org):
    """Create test AI system."""
    system = create_test_system(
        org_id=test_org.id,
        name="Test AI System",
        purpose="Testing document generation",
        domain="Education",
        owner_email="owner@test.com",
        deployment_context="Public-facing application",
        lifecycle_stage="Production",
        affected_users="Students and teachers",
        third_party_providers="OpenAI API",
        risk_category="High",
        ai_act_class="high-risk",
        impacts_fundamental_rights=True,
        uses_biometrics=False,
        uses_gpai=True
    )
    db_session.add(system)
    db_session.commit()
    return system


@pytest.fixture
def test_risks(db_session, test_org, test_system):
    """Create test risks."""
    risks = [
        AIRisk(
            org_id=test_org.id,
            system_id=test_system.id,
            description="Bias in training data",
            likelihood="M",
            impact="H",
            mitigation="Fairness metrics and bias testing",
            residual_risk="Low",
            owner_email="ml@test.com",
            priority="high"
        ),
        AIRisk(
            org_id=test_org.id,
            system_id=test_system.id,
            description="Data privacy breach",
            likelihood="L",
            impact="H",
            mitigation="Encryption and access controls",
            residual_risk="Medium",
            owner_email="security@test.com",
            priority="high"
        )
    ]
    for risk in risks:
        db_session.add(risk)
    db_session.commit()
    return risks


@pytest.fixture
def test_controls(db_session, test_org, test_system):
    """Create test controls."""
    controls = [
        Control(
            org_id=test_org.id,
            system_id=test_system.id,
            iso_clause="A.5.1",
            name="Leadership and commitment",
            priority="high",
            status="implemented",
            owner_email="ceo@test.com",
            rationale="Governance objectives approved by board"
        ),
        Control(
            org_id=test_org.id,
            system_id=test_system.id,
            iso_clause="A.6.1",
            name="Risk management",
            priority="high",
            status="implemented",
            owner_email="risk@test.com",
            rationale="Process aligned with ISO 31000"
        )
    ]
    for control in controls:
        db_session.add(control)
    db_session.commit()
    return controls


@pytest.fixture
def test_oversight(db_session, test_org, test_system):
    """Create test oversight."""
    oversight = Oversight(
        org_id=test_org.id,
        system_id=test_system.id,
        oversight_mode="in_the_loop",
        intervention_rules="Human review required for high-risk decisions",
        manual_override=True,
        appeals_channel="appeals@test.com",
        appeals_sla_days=3,
        appeals_responsible_email="support@test.com",
        ethics_committee=True,
        training_plan="Quarterly ethics training for all staff",
        comm_plan="Monthly stakeholder communication",
        external_disclosure=True
    )
    db_session.add(oversight)
    db_session.commit()
    return oversight


@pytest.fixture
def test_pmm(db_session, test_org, test_system):
    """Create test PMM."""
    pmm = PMM(
        org_id=test_org.id,
        system_id=test_system.id,
        logging_scope="All system inputs, outputs, and decision logs",
        retention_months=24,
        drift_threshold="5%",
        fairness_metrics="Accuracy, precision, recall, F1-score",
        incident_tool="Jira",
        audit_frequency="quarterly",
        management_review_frequency="semiannual",
        improvement_plan="Continuous improvement based on monitoring results",
        eu_db_required=True,
        eu_db_status="pending"
    )
    db_session.add(pmm)
    db_session.commit()
    return pmm


@pytest.fixture
def test_evidence(db_session, test_org, test_system, test_controls):
    """Create test evidence."""
    evidence = [
        Evidence(
            org_id=test_org.id,
            system_id=test_system.id,
            control_id=test_controls[0].id,
            label="Governance Policy",
            file_path="/evidence/governance.pdf",
            version="1.0",
            checksum="a1b2c3d4e5f6",
            iso42001_clause="A.5.1"
        ),
        Evidence(
            org_id=test_org.id,
            system_id=test_system.id,
            control_id=test_controls[1].id,
            label="Risk Assessment",
            file_path="/evidence/risk_assessment.pdf",
            version="2.1",
            checksum="f6e5d4c3b2a1",
            iso42001_clause="A.6.1"
        )
    ]
    for ev in evidence:
        db_session.add(ev)
    db_session.commit()
    return evidence


def test_build_system_context_complete(db_session, test_org, test_system, test_risks, test_controls, test_oversight, test_pmm, test_evidence):
    """Test building complete system context."""
    service = DocumentContextService(db_session)
    context = service.build_system_context(test_system.id, test_org.id)
    
    # Test company data
    assert context["company"]["name"] == "Test Company"
    assert context["company"]["primary_contact_name"] == "John Doe"
    assert context["company"]["org_role"] == "provider"
    
    # Test system data
    assert context["system"]["name"] == "Test AI System"
    assert context["system"]["purpose"] == "Testing document generation"
    assert context["system"]["domain"] == "Education"
    assert context["system"]["ai_act_class"] == "high-risk"
    assert context["system"]["requires_fria"] == True  # impacts_fundamental_rights=True
    
    # Test risks
    assert len(context["risks"]) == 2
    assert context["risks"][0]["description"] == "Bias in training data"
    assert context["risks"][0]["likelihood"] == "M"
    assert context["risks"][0]["impact"] == "H"
    
    # Test controls
    assert len(context["controls"]) == 2
    assert context["controls"][0]["iso_clause"] == "A.5.1"
    assert context["controls"][0]["name"] == "Leadership and commitment"
    assert context["controls"][0]["status"] == "implemented"
    assert len(context["controls"][0]["evidence"]) == 1  # One evidence linked
    
    # Test oversight
    assert context["oversight"]["mode"] == "in_the_loop"
    assert context["oversight"]["intervention_rules"] == "Human review required for high-risk decisions"
    assert context["oversight"]["ethics_committee"] == True
    
    # Test PMM
    assert context["pmm"]["logging_scope"] == "All system inputs, outputs, and decision logs"
    assert context["pmm"]["retention_months"] == 24
    assert context["pmm"]["drift_threshold"] == "5%"
    assert context["pmm"]["eu_db_required"] == True
    
    # Test evidence
    assert len(context["evidence"]) == 2
    assert context["evidence"][0]["label"] == "Governance Policy"
    assert context["evidence"][0]["checksum"] == "a1b2c3d4e5f6"
    
    # Test metadata
    assert context["metadata"]["system_id"] == test_system.id
    assert context["metadata"]["has_risks"] == True
    assert context["metadata"]["has_controls"] == True
    assert context["metadata"]["has_evidence"] == True
    assert context["metadata"]["risk_count"] == 2
    assert context["metadata"]["control_count"] == 2
    assert context["metadata"]["evidence_count"] == 2


def test_build_system_context_minimal(db_session, test_org, test_system):
    """Test building context with minimal data (no risks, controls, etc.)."""
    service = DocumentContextService(db_session)
    context = service.build_system_context(test_system.id, test_org.id)
    
    # Should still have system and company data
    assert context["system"]["name"] == "Test AI System"
    assert context["company"]["name"] == "Test Company"
    
    # Should have empty arrays for missing data
    assert len(context["risks"]) == 0
    assert len(context["controls"]) == 0
    assert len(context["evidence"]) == 0
    
    # Should have default values for missing oversight/PMM
    assert context["oversight"]["mode"] == "in_the_loop"  # default
    assert context["pmm"]["retention_months"] == 12  # default
    assert context["pmm"]["drift_threshold"] == "10%"  # default
    
    # Metadata should reflect missing data
    assert context["metadata"]["has_risks"] == False
    assert context["metadata"]["has_controls"] == False
    assert context["metadata"]["has_evidence"] == False


def test_requires_fria_computation(db_session, test_org):
    """Test FRIA requirement computation."""
    service = DocumentContextService(db_session)
    
    # System with fundamental rights impact
    system1 = create_test_system(
        org_id=test_org.id,
        name="System 1",
        impacts_fundamental_rights=True,
        ai_act_class="minimal"
    )
    db_session.add(system1)
    db_session.commit()
    
    # System with biometrics
    system2 = create_test_system(
        org_id=test_org.id,
        name="System 2",
        uses_biometrics=True,
        ai_act_class="minimal"
    )
    db_session.add(system2)
    db_session.commit()
    
    # System with high-risk classification
    system3 = create_test_system(
        org_id=test_org.id,
        name="System 3",
        ai_act_class="high-risk"
    )
    db_session.add(system3)
    db_session.commit()
    
    # System that doesn't require FRIA
    system4 = create_test_system(
        org_id=test_org.id,
        name="System 4",
        ai_act_class="minimal"
    )
    db_session.add(system4)
    db_session.commit()
    
    # Test context building for each
    context1 = service.build_system_context(system1.id, test_org.id)
    context2 = service.build_system_context(system2.id, test_org.id)
    context3 = service.build_system_context(system3.id, test_org.id)
    context4 = service.build_system_context(system4.id, test_org.id)
    
    assert context1["system"]["requires_fria"] == True  # fundamental rights
    assert context2["system"]["requires_fria"] == True  # biometrics
    assert context3["system"]["requires_fria"] == True  # high-risk
    assert context4["system"]["requires_fria"] == False  # none of the above


def test_evidence_citations(db_session, test_org, test_system):
    """Test evidence citation generation."""
    service = DocumentContextService(db_session)
    
    # Create evidence with checksums
    evidence1 = Evidence(
        org_id=test_org.id,
        system_id=test_system.id,
        label="Test Evidence 1",
        checksum="a1b2c3d4e5f6789"
    )
    evidence2 = Evidence(
        org_id=test_org.id,
        system_id=test_system.id,
        label="Test Evidence 2",
        checksum=""
    )
    
    db_session.add_all([evidence1, evidence2])
    db_session.commit()
    
    citations = service.get_evidence_citations([evidence1, evidence2])
    
    assert evidence1.id in citations
    assert evidence2.id in citations
    assert "EV-" in citations[evidence1.id]
    assert "sha256:a1b2c3d4e5f6" in citations[evidence1.id]  # truncated checksum
    assert "sha256:" not in citations[evidence2.id]  # no checksum
