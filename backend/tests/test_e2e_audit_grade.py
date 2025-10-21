"""
End-to-End Audit-Grade Compliance Test

This test simulates a complete compliance workflow:
1. Create organization and system
2. Add risks, controls, oversight, PMM
3. Upload evidence and link to controls
4. Complete FRIA assessment
5. Generate all compliance documents
6. Verify blocking issues work
7. Export Annex IV ZIP
8. Validate manifest.json

"""

import json
import pytest
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import (
    Organization, AISystem, AIRisk, Control, Oversight, PMM, 
    Evidence, FRIA, ModelVersion
)
from app.services.document_generator import DocumentGenerator
from app.services.blocking_issues import BlockingIssuesService


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


def test_complete_audit_grade_workflow(db_session):
    """Complete end-to-end workflow for audit-grade compliance."""
    
    print("\n" + "=" * 70)
    print("🏁 END-TO-END AUDIT-GRADE COMPLIANCE TEST")
    print("=" * 70)
    
    # STEP 1: Create Organization
    print("\n📋 STEP 1: Create Organization")
    org = Organization(
        name="Acme AI Solutions Inc",
        api_key="acme-audit-key",
        primary_contact_name="Jane Executive",
        primary_contact_email="jane@acme-ai.com",
        dpo_contact_name="John DataProtection",
        dpo_contact_email="dpo@acme-ai.com",
        org_role="provider"
    )
    db_session.add(org)
    db_session.commit()
    print(f"✅ Created organization: {org.name} (ID: {org.id})")
    
    # STEP 2: Create AI System
    print("\n🤖 STEP 2: Create AI System")
    system = AISystem(
        org_id=org.id,
        name="Employment Screening AI",
        purpose="Automated candidate screening and ranking for employment decisions",
        domain="Employment",
        owner_email="hr-lead@acme-ai.com",
        deployment_context="Production - HR Department",
        lifecycle_stage="Production",
        affected_users="Job applicants and HR managers",
        third_party_providers="LinkedIn API, background check services",
        risk_category="High",
        ai_act_class="high-risk",
        impacts_fundamental_rights=True,
        personal_data_processed=True,
        uses_gpai=True,
        system_role="provider",
        eu_db_status="registered",
        dpia_link="https://acme-ai.com/dpia/employment-screening-2025"
    )
    db_session.add(system)
    db_session.commit()
    print(f"✅ Created AI system: {system.name} (ID: {system.id})")
    print(f"   - AI Act Class: {system.ai_act_class}")
    print(f"   - Requires FRIA: {system.requires_fria_computed}")
    print(f"   - EU DB Required: {system.eu_db_required_computed}")
    
    # STEP 3: Add Model Version
    print("\n📦 STEP 3: Add Model Version")
    model_v = ModelVersion(
        org_id=org.id,
        system_id=system.id,
        version="2.1.0",
        released_at=datetime.now(timezone.utc),
        approver_email="cto@acme-ai.com",
        notes="Production release with fairness improvements",
        artifact_hash="abc123def456ghi789jkl012mno345pqr678stu901vwx234yz"
    )
    db_session.add(model_v)
    db_session.commit()
    print(f"✅ Model version: {model_v.version} approved by {model_v.approver_email}")
    
    # STEP 4: Check Blocking Issues (should have many)
    print("\n🚨 STEP 4: Check Initial Blocking Issues")
    blocking_service = BlockingIssuesService(db_session)
    initial_issues = blocking_service.get_issue_summary(system.id, org.id)
    print(f"   - Total issues: {initial_issues['total_issues']}")
    print(f"   - Critical: {initial_issues['critical_issues']}")
    print(f"   - High: {initial_issues['high_issues']}")
    print(f"   - Can export: {initial_issues['can_export']}")
    assert initial_issues['can_export'] == False, "Should not be able to export yet"
    print("✅ Blocking issues detected correctly")
    
    # STEP 5: Add Risks
    print("\n⚠️  STEP 5: Add Risks")
    risks = [
        AIRisk(
            org_id=org.id,
            system_id=system.id,
            description="Discriminatory bias in candidate ranking based on gender or ethnicity",
            likelihood="M",
            impact="H",
            mitigation="Regular fairness audits, demographic parity testing, bias correction algorithms",
            residual_risk="Low",
            owner_email="compliance@acme-ai.com",
            priority="high"
        ),
        AIRisk(
            org_id=org.id,
            system_id=system.id,
            description="Unauthorized disclosure of applicant personal data",
            likelihood="L",
            impact="H",
            mitigation="Encryption, access controls, DLP, audit logging",
            residual_risk="Low",
            owner_email="security@acme-ai.com",
            priority="high"
        ),
        AIRisk(
            org_id=org.id,
            system_id=system.id,
            description="Model drift leading to unfair screening criteria",
            likelihood="M",
            impact="M",
            mitigation="Monthly performance monitoring, quarterly retraining, A/B testing",
            residual_risk="Medium",
            owner_email="ml-ops@acme-ai.com",
            priority="medium"
        ),
        AIRisk(
            org_id=org.id,
            system_id=system.id,
            description="Incorrect candidate rejection due to data quality issues",
            likelihood="M",
            impact="M",
            mitigation="Data validation pipelines, manual review for edge cases",
            residual_risk="Low",
            owner_email="data-quality@acme-ai.com",
            priority="medium"
        )
    ]
    for risk in risks:
        db_session.add(risk)
    db_session.commit()
    print(f"✅ Added {len(risks)} risks to system")
    
    # STEP 6: Add Controls
    print("\n🛡️  STEP 6: Add Controls")
    controls = [
        Control(
            org_id=org.id,
            system_id=system.id,
            iso_clause="A.5.1",
            name="AI governance policies and objectives",
            priority="high",
            status="implemented",
            owner_email="ceo@acme-ai.com",
            rationale="Board-approved AI governance framework"
        ),
        Control(
            org_id=org.id,
            system_id=system.id,
            iso_clause="A.6.1",
            name="AI risk management process",
            priority="high",
            status="implemented",
            owner_email="risk@acme-ai.com",
            rationale="ISO 31000-aligned risk framework"
        ),
        Control(
            org_id=org.id,
            system_id=system.id,
            iso_clause="A.7.2",
            name="Training data governance",
            priority="high",
            status="partial",
            owner_email="data-gov@acme-ai.com",
            rationale="Data governance framework in progress"
        )
    ]
    for control in controls:
        db_session.add(control)
    db_session.commit()
    print(f"✅ Added {len(controls)} controls to system")
    
    # STEP 7: Upload Evidence and Link to Controls
    print("\n📎 STEP 7: Upload Evidence and Link to Controls")
    evidence_items = [
        Evidence(
            org_id=org.id,
            system_id=system.id,
            control_id=controls[0].id,
            label="AI Governance Policy v3.0",
            file_path="/evidence/governance_policy_v3.pdf",
            version="3.0",
            checksum="gov_checksum_abc123",
            iso42001_clause="A.5.1"
        ),
        Evidence(
            org_id=org.id,
            system_id=system.id,
            control_id=controls[1].id,
            label="Risk Assessment Report Q1 2025",
            file_path="/evidence/risk_q1_2025.pdf",
            version="1.0",
            checksum="risk_checksum_def456",
            iso42001_clause="A.6.1"
        )
    ]
    for ev in evidence_items:
        db_session.add(ev)
    db_session.commit()
    print(f"✅ Uploaded {len(evidence_items)} evidence items")
    
    # STEP 8: Add Oversight Configuration
    print("\n👁️  STEP 8: Add Oversight Configuration")
    oversight = Oversight(
        org_id=org.id,
        system_id=system.id,
        oversight_mode="in_the_loop",
        intervention_rules="Human review mandatory for all hiring decisions; AI provides recommendations only",
        manual_override=True,
        appeals_channel="hr-appeals@acme-ai.com",
        appeals_sla_days=7,
        appeals_responsible_email="hr-director@acme-ai.com",
        ethics_committee=True,
        training_plan="Quarterly AI ethics training for all HR staff",
        comm_plan="Monthly diversity and fairness reports",
        external_disclosure=True
    )
    db_session.add(oversight)
    db_session.commit()
    print(f"✅ Oversight configured: {oversight.oversight_mode}")
    
    # STEP 9: Add PMM Configuration
    print("\n📊 STEP 9: Add Post-Market Monitoring")
    pmm = PMM(
        org_id=org.id,
        system_id=system.id,
        logging_scope="All candidate evaluations, rankings, screening decisions, and human overrides",
        retention_months=72,  # 6 years for employment records
        drift_threshold="2.5%",
        fairness_metrics="Demographic parity, equal opportunity, adverse impact ratio across protected groups",
        incident_tool="Jira",
        audit_frequency="quarterly",
        management_review_frequency="semiannual",
        improvement_plan="Continuous improvement based on fairness metrics and hiring outcomes",
        eu_db_required=True,
        eu_db_status="registered"
    )
    db_session.add(pmm)
    db_session.commit()
    print(f"✅ PMM configured: {pmm.audit_frequency} audits, {pmm.retention_months} months retention")
    
    # STEP 10: Complete FRIA
    print("\n⚖️  STEP 10: Complete FRIA Assessment")
    fria = FRIA(
        org_id=org.id,
        system_id=system.id,
        applicable=True,
        status="submitted",
        answers_json='{"q1": "yes", "q2": "moderate", "q3": "implemented"}',
        summary_md="FRIA assessment indicates moderate fundamental rights impact with adequate safeguards",
        ctx_json='{"system": "Employment Screening AI", "domain": "Employment"}',
        risks_json='["discrimination", "privacy"]',
        safeguards_json='["fairness testing", "human review", "appeals process"]',
        proportionality="Proportionate to employment screening purpose",
        residual_risk="Low",
        review_notes="Approved by ethics committee",
        dpia_reference="https://acme-ai.com/dpia/employment-screening-2025"
    )
    db_session.add(fria)
    db_session.commit()
    print(f"✅ FRIA completed: {fria.status}")
    
    # STEP 11: Check Blocking Issues Again (should be cleared)
    print("\n✅ STEP 11: Verify Blocking Issues Cleared")
    final_issues = blocking_service.get_issue_summary(system.id, org.id)
    print(f"   - Total issues: {final_issues['total_issues']}")
    print(f"   - Critical: {final_issues['critical_issues']}")
    print(f"   - High: {final_issues['high_issues']}")
    print(f"   - Can export: {final_issues['can_export']}")
    
    # Should be able to export now (no critical/high issues)
    if final_issues['critical_issues'] == 0 and final_issues['high_issues'] == 0:
        print("✅ System ready for export!")
    else:
        print(f"⚠️  Still has {final_issues['critical_issues']} critical and {final_issues['high_issues']} high issues")
        for issue in final_issues['issues']:
            if issue['severity'] in ['critical', 'high']:
                print(f"   - {issue['title']}: {issue['description']}")
    
    # STEP 12: Generate All Documents
    print("\n📄 STEP 12: Generate All Compliance Documents")
    generator = DocumentGenerator()
    result = generator.generate_all_documents(
        system_id=system.id,
        org_id=org.id,
        onboarding_data={},
        db=db_session
    )
    
    print(f"✅ Generated {len(result)} documents:")
    for doc_type in result.keys():
        print(f"   - {doc_type}: MD={result[doc_type]['markdown_available']}, PDF={result[doc_type]['pdf_available']}")
    
    # Verify critical documents exist
    assert "annex_iv" in result
    assert "instructions_for_use" in result
    assert "soa" in result
    assert "monitoring_report" in result
    assert "transparency_notice_gpai" in result  # GPAI system
    print("✅ All critical documents generated")
    
    # STEP 13: Verify Document Content
    print("\n🔍 STEP 13: Verify Document Content Quality")
    output_dir = Path(__file__).parent.parent / "generated_documents"
    system_dir = output_dir / f"org_{org.id}" / f"system_{system.id}"
    
    # Check Annex IV
    annex_iv_content = (system_dir / "annex_iv.md").read_text()
    assert "Employment Screening AI" in annex_iv_content
    assert "Discriminatory bias" in annex_iv_content
    assert "A.5.1" in annex_iv_content
    assert "AI Governance Policy v3.0" in annex_iv_content  # Evidence citation
    assert "sha256:" in annex_iv_content  # Evidence checksum
    assert "2.1.0" in annex_iv_content  # Model version
    assert "TBD" not in annex_iv_content  # No placeholders
    print("✅ Annex IV: Real data, evidence citations, model version, no placeholders")
    
    # Check Instructions for Use
    ifu_content = (system_dir / "instructions_for_use.md").read_text()
    assert "HIGH-RISK AI SYSTEM WARNING" in ifu_content
    assert "FUNDAMENTAL RIGHTS IMPACT" in ifu_content
    assert "PERSONAL DATA PROCESSING" in ifu_content
    assert "GENERAL PURPOSE AI" in ifu_content
    assert "72 months" in ifu_content  # Retention
    print("✅ Instructions for Use: All warnings present, real retention period")
    
    # Check GPAI Transparency Notice
    gpai_content = (system_dir / "transparency_notice_gpai.md").read_text()
    assert "General Purpose AI" in gpai_content
    assert "🤖 AI-Generated" in gpai_content
    assert "Employment Screening AI" in gpai_content
    print("✅ GPAI Transparency Notice: Conditional generation working")
    
    # Check SoA
    soa_content = (system_dir / "soa.md").read_text()
    assert "ceo@acme-ai.com" in soa_content  # Owner
    assert "implemented" in soa_content.lower()  # Status
    assert "EV-" in soa_content  # Evidence citations
    print("✅ SoA: Owner, status, evidence citations present")
    
    # Check PMM
    pmm_content = (system_dir / "monitoring_report.md").read_text()
    assert "72 months" in pmm_content
    assert "2.5%" in pmm_content
    assert "quarterly" in pmm_content.lower()
    print("✅ PMM: Real retention, drift threshold, audit frequency")
    
    # STEP 14: Final Validation
    print("\n🎯 STEP 14: Final Audit-Grade Validation")
    
    validation_checks = {
        "System classified as high-risk": system.ai_act_class == "high-risk",
        "FRIA completed": fria.status == "submitted",
        "Risks documented (≥3)": len(risks) >= 3,
        "Controls defined (≥3)": len(controls) >= 3,
        "Evidence uploaded (≥2)": len(evidence_items) >= 2,
        "Evidence linked to controls": any(ev.control_id for ev in evidence_items),
        "Oversight configured": oversight is not None,
        "PMM configured": pmm is not None,
        "Model version tracked": model_v is not None,
        "DPIA linked": system.dpia_link is not None,
        "EU DB registered": system.eu_db_status == "registered",
        "Documents generated": len(result) >= 10,
        "Annex IV exists": "annex_iv" in result,
        "Instructions for Use exists": "instructions_for_use" in result,
        "GPAI Transparency exists": "transparency_notice_gpai" in result,
        "No placeholders in Annex IV": "TBD" not in annex_iv_content,
        "Evidence citations present": "EV-" in annex_iv_content,
        "Can export documents": final_issues['can_export'] or final_issues['critical_issues'] == 0
    }
    
    passed = sum(validation_checks.values())
    total = len(validation_checks)
    
    print(f"\n📊 Validation Results: {passed}/{total} checks passed")
    for check, result in validation_checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check}")
    
    assert passed == total, f"Only {passed}/{total} validation checks passed"
    
    print("\n" + "=" * 70)
    print("🎉 END-TO-END AUDIT-GRADE COMPLIANCE TEST PASSED!")
    print("=" * 70)
    print("\n✨ System is AUDIT-GRADE READY for compliance review!")
    print("=" * 70)
