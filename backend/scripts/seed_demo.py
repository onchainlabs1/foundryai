"""
Demo data seeding script for AIMS Readiness platform.

Creates 4 sample AI systems with realistic data:
1. VisionID - High-risk facial recognition system
2. CreditAssist - High-risk credit scoring system
3. ChatAssist-G - GPAI chatbot (limited risk)
4. OpsForecast - Minimal risk internal forecasting

Usage:
    python -m scripts.seed_demo
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

from app.database import Base, SessionLocal, engine
from app.models import FRIA, AISystem, Control, Evidence, Incident, Organization

logger = logging.getLogger(__name__)


def seed_demo_data():
    """Seed the database with demo data."""
    logger.info("🌱 Starting demo data seeding...")

    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if demo org already exists
        demo_org = db.query(Organization).filter(
            Organization.api_key == "dev-aims-demo-key"
        ).first()

        if not demo_org:
            demo_org = Organization(
                name="AIMS Demo Corporation",
                api_key="dev-aims-demo-key"
            )
            db.add(demo_org)
            db.commit()
            db.refresh(demo_org)
            logger.info(f"✓ Created demo organization: {demo_org.name}")
        else:
            logger.info(f"✓ Demo organization already exists: {demo_org.name}")

        # Clear existing demo data for clean slate
        db.query(Incident).filter(Incident.org_id == demo_org.id).delete()
        db.query(FRIA).filter(FRIA.org_id == demo_org.id).delete()
        db.query(Control).filter(Control.org_id == demo_org.id).delete()
        db.query(Evidence).filter(Evidence.org_id == demo_org.id).delete()
        db.query(AISystem).filter(AISystem.org_id == demo_org.id).delete()
        db.commit()
        logger.info("✓ Cleared existing demo data")

        # System 1: VisionID (High-Risk)
        vision_id = AISystem(
            org_id=demo_org.id,
            name="VisionID v2.1",
            purpose="Facial recognition system for public security and access control",
            domain="Security & Surveillance",
            owner_email="security@aimsdemo.com",
            deployment_context="public",
            uses_biometrics=True,
            is_general_purpose_ai=False,
            impacts_fundamental_rights=True,
            personal_data_processed=True,
            training_data_sensitivity="high",
            output_type="classification",
            criticality="high",
            ai_act_class="high",
            notes="High-risk biometric identification system deployed in public spaces"
        )
        db.add(vision_id)

        # System 2: CreditAssist (High-Risk)
        credit_assist = AISystem(
            org_id=demo_org.id,
            name="CreditAssist v3.5",
            purpose="AI-powered credit scoring and loan approval system",
            domain="Financial Services",
            owner_email="finance@aimsdemo.com",
            deployment_context="production",
            uses_biometrics=False,
            is_general_purpose_ai=False,
            impacts_fundamental_rights=True,
            personal_data_processed=True,
            training_data_sensitivity="high",
            output_type="prediction",
            criticality="high",
            ai_act_class="high",
            notes="Automated credit decision system affecting access to financial services"
        )
        db.add(credit_assist)

        # System 3: ChatAssist-G (GPAI - Limited)
        chat_assist = AISystem(
            org_id=demo_org.id,
            name="ChatAssist-G v1.8",
            purpose="General purpose conversational AI assistant for customer support",
            domain="Customer Service",
            owner_email="product@aimsdemo.com",
            deployment_context="production",
            uses_biometrics=False,
            is_general_purpose_ai=True,
            impacts_fundamental_rights=False,
            personal_data_processed=True,
            training_data_sensitivity="medium",
            output_type="text_generation",
            criticality="medium",
            ai_act_class="limited",
            notes="GPAI system with broad conversational capabilities"
        )
        db.add(chat_assist)

        # System 4: OpsForecast (Minimal)
        ops_forecast = AISystem(
            org_id=demo_org.id,
            name="OpsForecast v1.2",
            purpose="Internal operations forecasting and resource optimization",
            domain="Operations",
            owner_email="ops@aimsdemo.com",
            deployment_context="internal",
            uses_biometrics=False,
            is_general_purpose_ai=False,
            impacts_fundamental_rights=False,
            personal_data_processed=False,
            training_data_sensitivity="low",
            output_type="prediction",
            criticality="low",
            ai_act_class="minimal",
            notes="Internal-only forecasting tool with minimal risk"
        )
        db.add(ops_forecast)

        db.commit()
        db.refresh(vision_id)
        db.refresh(credit_assist)
        db.refresh(chat_assist)
        db.refresh(ops_forecast)
        logger.info("✓ Created 4 AI systems")

        # Add Controls for VisionID (High-Risk)
        vision_controls = [
            Control(
                org_id=demo_org.id,
                system_id=vision_id.id,
                iso_clause="ISO42001:6.1",
                name="Risk Management Process",
                priority="high",
                status="implemented",
                owner_email="security@aimsdemo.com",
                due_date=(datetime.now(timezone.utc) + timedelta(days=30)).date(),
                rationale="Critical for high-risk biometric system"
            ),
            Control(
                org_id=demo_org.id,
                system_id=vision_id.id,
                iso_clause="ISO42001:6.2.2",
                name="Data Quality Management",
                priority="high",
                status="partial",
                owner_email="data@aimsdemo.com",
                due_date=(datetime.now(timezone.utc) + timedelta(days=5)).date(),
                rationale="Ensuring training data quality and bias mitigation"
            ),
            Control(
                org_id=demo_org.id,
                system_id=vision_id.id,
                iso_clause="ISO42001:7.2",
                name="Human Oversight Mechanism",
                priority="high",
                status="implemented",
                owner_email="security@aimsdemo.com",
                due_date=(datetime.now(timezone.utc) + timedelta(days=60)).date(),
                rationale="Required for high-risk public deployment"
            ),
            Control(
                org_id=demo_org.id,
                system_id=vision_id.id,
                iso_clause="ISO42001:8.1",
                name="Logging and Traceability",
                priority="medium",
                status="missing",
                owner_email="compliance@aimsdemo.com",
                due_date=(datetime.now(timezone.utc) + timedelta(days=3)).date(),
                rationale="Article 12 AI Act requirement"
            ),
        ]

        # Add Controls for CreditAssist
        credit_controls = [
            Control(
                org_id=demo_org.id,
                system_id=credit_assist.id,
                iso_clause="ISO42001:6.1",
                name="Risk Management Process",
                priority="high",
                status="implemented",
                owner_email="finance@aimsdemo.com",
                due_date=(datetime.now(timezone.utc) + timedelta(days=45)).date(),
                rationale="Financial services compliance"
            ),
            Control(
                org_id=demo_org.id,
                system_id=credit_assist.id,
                iso_clause="ISO42001:6.2.3",
                name="Bias Testing and Mitigation",
                priority="high",
                status="partial",
                owner_email="ml@aimsdemo.com",
                due_date=(datetime.now(timezone.utc) + timedelta(days=2)).date(),
                rationale="Prevent discriminatory lending decisions"
            ),
            Control(
                org_id=demo_org.id,
                system_id=credit_assist.id,
                iso_clause="ISO42001:7.1",
                name="Transparency and Explainability",
                priority="high",
                status="implemented",
                owner_email="compliance@aimsdemo.com",
                due_date=(datetime.now(timezone.utc) + timedelta(days=90)).date(),
                rationale="Right to explanation for credit decisions"
            ),
        ]

        # Add Controls for ChatAssist-G
        chat_controls = [
            Control(
                org_id=demo_org.id,
                system_id=chat_assist.id,
                iso_clause="ISO42001:6.1",
                name="Risk Management Process",
                priority="medium",
                status="implemented",
                owner_email="product@aimsdemo.com",
                due_date=(datetime.now(timezone.utc) + timedelta(days=60)).date(),
                rationale="GPAI risk management"
            ),
            Control(
                org_id=demo_org.id,
                system_id=chat_assist.id,
                iso_clause="ISO42001:8.2",
                name="Content Moderation",
                priority="medium",
                status="implemented",
                owner_email="safety@aimsdemo.com",
                due_date=(datetime.now(timezone.utc) + timedelta(days=30)).date(),
                rationale="Prevent harmful outputs"
            ),
        ]

        # Add Controls for OpsForecast
        ops_controls = [
            Control(
                org_id=demo_org.id,
                system_id=ops_forecast.id,
                iso_clause="ISO42001:6.1",
                name="Risk Management Process",
                priority="low",
                status="implemented",
                owner_email="ops@aimsdemo.com",
                due_date=(datetime.now(timezone.utc) + timedelta(days=120)).date(),
                rationale="Basic risk management for internal system"
            ),
        ]

        db.add_all(vision_controls + credit_controls + chat_controls + ops_controls)
        db.commit()
        logger.info(f"✓ Created {len(vision_controls + credit_controls + chat_controls + ops_controls)} controls")

        # Add Evidence
        evidence_items = [
            Evidence(
                org_id=demo_org.id,
                system_id=vision_id.id,
                label="Risk Assessment Report Q4 2024",
                file_path="evidence/vision_id_risk_assessment_q4_2024.pdf",
                checksum="a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
                uploaded_by="security@aimsdemo.com",
                iso42001_clause="ISO42001:6.1",
                control_name="Risk Management Process",
                status="uploaded"
            ),
            Evidence(
                org_id=demo_org.id,
                system_id=vision_id.id,
                label="Human Oversight Procedures",
                file_path="evidence/vision_id_human_oversight.pdf",
                checksum="b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7",
                uploaded_by="security@aimsdemo.com",
                iso42001_clause="ISO42001:7.2",
                control_name="Human Oversight Mechanism",
                status="uploaded"
            ),
            Evidence(
                org_id=demo_org.id,
                system_id=credit_assist.id,
                label="Bias Testing Results 2024",
                file_path="evidence/credit_assist_bias_testing.pdf",
                checksum="c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8",
                uploaded_by="ml@aimsdemo.com",
                iso42001_clause="ISO42001:6.2.3",
                control_name="Bias Testing and Mitigation",
                status="uploaded"
            ),
            Evidence(
                org_id=demo_org.id,
                system_id=credit_assist.id,
                label="Explainability Framework Documentation",
                file_path="evidence/credit_assist_explainability.pdf",
                checksum="d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9",
                uploaded_by="compliance@aimsdemo.com",
                iso42001_clause="ISO42001:7.1",
                control_name="Transparency and Explainability",
                status="uploaded"
            ),
        ]

        db.add_all(evidence_items)
        db.commit()
        logger.info(f"✓ Created {len(evidence_items)} evidence records")

        # Add FRIA for VisionID (High-Risk)
        vision_fria = FRIA(
            org_id=demo_org.id,
            system_id=vision_id.id,
            applicable=True,
            status="approved",
            answers_json=str({
                "biometric_data": "Yes",
                "fundamental_rights": "Yes",
                "critical_infrastructure": "Yes",
                "vulnerable_groups": "No",
                "automated_decisions": "Yes",
                "human_oversight": "Yes",
                "subjects_informed": "Yes",
                "explainable_contestable": "Partial",
                "dpia_exists": "Yes",
                "bias_safeguards": "Yes"
            }),
            summary_md="""# Fundamental Rights Impact Assessment (FRIA)

Applicable: Yes

## Answers
- biometric_data: Yes
- fundamental_rights: Yes
- critical_infrastructure: Yes
- vulnerable_groups: No
- automated_decisions: Yes
- human_oversight: Yes
- subjects_informed: Yes
- explainable_contestable: Partial
- dpia_exists: Yes
- bias_safeguards: Yes

Generated at: 2024-12-15T10:30:00Z"""
        )
        db.add(vision_fria)

        # Add FRIA for CreditAssist (High-Risk)
        credit_fria = FRIA(
            org_id=demo_org.id,
            system_id=credit_assist.id,
            applicable=True,
            status="submitted",
            answers_json=str({
                "biometric_data": "No",
                "fundamental_rights": "Yes",
                "critical_infrastructure": "No",
                "vulnerable_groups": "No",
                "automated_decisions": "Yes",
                "human_oversight": "Yes",
                "subjects_informed": "Yes",
                "explainable_contestable": "Yes",
                "dpia_exists": "Yes",
                "bias_safeguards": "Yes"
            }),
            summary_md="""# Fundamental Rights Impact Assessment (FRIA)

Applicable: Yes

## Answers
- biometric_data: No
- fundamental_rights: Yes
- critical_infrastructure: No
- vulnerable_groups: No
- automated_decisions: Yes
- human_oversight: Yes
- subjects_informed: Yes
- explainable_contestable: Yes
- dpia_exists: Yes
- bias_safeguards: Yes

Generated at: 2024-12-16T14:20:00Z"""
        )
        db.add(credit_fria)

        db.commit()
        logger.info("✓ Created 2 FRIA assessments")

        # Add Incidents
        incidents = [
            Incident(
                org_id=demo_org.id,
                system_id=vision_id.id,
                severity="medium",
                description="False positive rate increased by 3% in low-light conditions",
                detected_at=datetime.now(timezone.utc) - timedelta(days=15),
                resolved_at=datetime.now(timezone.utc) - timedelta(days=10),
                corrective_action="Updated image preprocessing pipeline and retrained model with augmented low-light dataset"
            ),
            Incident(
                org_id=demo_org.id,
                system_id=credit_assist.id,
                severity="high",
                description="Bias detected in credit scoring for certain demographic groups",
                detected_at=datetime.now(timezone.utc) - timedelta(days=5),
                resolved_at=None,
                corrective_action="Investigation ongoing. Temporary manual review implemented for affected cases."
            ),
            Incident(
                org_id=demo_org.id,
                system_id=chat_assist.id,
                severity="low",
                description="Occasional inappropriate responses detected in edge cases",
                detected_at=datetime.now(timezone.utc) - timedelta(days=20),
                resolved_at=datetime.now(timezone.utc) - timedelta(days=18),
                corrective_action="Enhanced content filtering rules and updated moderation model"
            ),
        ]

        db.add_all(incidents)
        db.commit()
        logger.info(f"✓ Created {len(incidents)} incidents")

        logger.info("\n✅ Demo data seeding completed successfully!")
        logger.info("\n📊 Summary:")
        logger.info(f"   - Organization: {demo_org.name}")
        logger.info(f"   - API Key: {demo_org.api_key}")
        logger.info("   - Systems: 4 (2 High-Risk, 1 GPAI, 1 Minimal)")
        logger.info(f"   - Controls: {len(vision_controls + credit_controls + chat_controls + ops_controls)}")
        logger.info(f"   - Evidence: {len(evidence_items)}")
        logger.info("   - FRIAs: 2")
        logger.info(f"   - Incidents: {len(incidents)} (1 open, 2 resolved)")
        logger.info("\n🚀 Ready to demo at: http://localhost:3002")
        logger.info(f"   Login with API key: {demo_org.api_key}")

    except Exception as e:
        logger.error(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()

