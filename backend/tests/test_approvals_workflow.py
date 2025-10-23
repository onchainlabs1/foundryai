"""
Test Document Approvals Workflow
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Organization, AISystem, DocumentApproval
from tests.conftest import create_test_system
from app.api.routes.approvals import (
    submit_document_for_review,
    approve_document,
    SubmitForReviewRequest,
    ApproveDocumentRequest
)


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
def test_system(db_session):
    """Create test organization and system."""
    org = Organization(
        name="Approval Test Corp",
        api_key="approval-test-key",
        org_role="provider"
    )
    db_session.add(org)
    db_session.commit()
    
    system = create_test_system(
        org_id=org.id,
        name="Approval Test System",
        purpose="Testing approvals workflow",
        ai_act_class="high-risk",
        impacts_fundamental_rights=True,
        requires_fria=True
    )
    db_session.add(system)
    db_session.commit()
    
    return {"org": org, "system": system}


def test_approval_workflow_complete(db_session, test_system):
    """Test complete approval workflow: draft → submitted → approved."""
    
    org = test_system["org"]
    system = test_system["system"]
    
    print("\n📋 APPROVALS WORKFLOW TEST")
    print("=" * 60)
    
    # STEP 1: Submit for review
    print("\n1️⃣  Submit Annex IV for Review")
    submit_req = SubmitForReviewRequest(
        doc_type="annex_iv",
        submitted_by="author@approval-test.com",
        notes="Please review Annex IV documentation"
    )
    
    submission = submit_document_for_review(
        system_id=system.id,
        payload=submit_req,
        org=org,
        db=db_session
    )
    
    assert submission.status == "submitted"
    assert submission.submitted_by == "author@approval-test.com"
    assert submission.doc_type == "annex_iv"
    print(f"✅ Document submitted by {submission.submitted_by}")
    print(f"   Status: {submission.status}")
    
    # STEP 2: Verify in database
    print("\n2️⃣  Verify Approval Record in Database")
    approval_db = (
        db_session.query(DocumentApproval)
        .filter(
            DocumentApproval.org_id == org.id,
            DocumentApproval.system_id == system.id,
            DocumentApproval.doc_type == "annex_iv"
        )
        .first()
    )
    
    assert approval_db is not None
    assert approval_db.status == "submitted"
    print(f"✅ Approval record exists in database (ID: {approval_db.id})")
    
    # STEP 3: Approve document
    print("\n3️⃣  Approve Document")
    approve_req = ApproveDocumentRequest(
        approver_email="manager@approval-test.com",
        notes="Approved - documentation complete"
    )
    
    approved = approve_document(
        system_id=system.id,
        doc_type="annex_iv",
        payload=approve_req,
        org=org,
        db=db_session
    )
    
    assert approved.status == "approved"
    assert approved.approver_email == "manager@approval-test.com"
    assert approved.approved_at is not None
    print(f"✅ Document approved by {approved.approver_email}")
    print(f"   Approved at: {approved.approved_at}")
    
    # STEP 4: Verify approval persisted
    print("\n4️⃣  Verify Approval Persisted")
    db_session.refresh(approval_db)
    
    assert approval_db.status == "approved"
    assert approval_db.approver_email == "manager@approval-test.com"
    print(f"✅ Approval status updated in database")
    
    # STEP 5: Test idempotent submission (resubmit should update, not create new)
    print("\n5️⃣  Test Idempotent Submission")
    resubmit_req = SubmitForReviewRequest(
        doc_type="annex_iv",
        submitted_by="author2@approval-test.com",
        notes="Resubmitting with updates"
    )
    
    resubmission = submit_document_for_review(
        system_id=system.id,
        payload=resubmit_req,
        org=org,
        db=db_session
    )
    
    # Should be same ID (updated, not new)
    assert resubmission.id == approval_db.id
    assert resubmission.status == "submitted"  # Back to submitted
    assert resubmission.submitted_by == "author2@approval-test.com"
    print(f"✅ Resubmission updated existing record (ID: {resubmission.id})")
    
    # Verify count is still 1
    count = (
        db_session.query(DocumentApproval)
        .filter(
            DocumentApproval.org_id == org.id,
            DocumentApproval.system_id == system.id,
            DocumentApproval.doc_type == "annex_iv"
        )
        .count()
    )
    assert count == 1
    print(f"✅ Only 1 approval record exists (idempotent)")
    
    print("\n" + "=" * 60)
    print("🎉 APPROVAL WORKFLOW TEST PASSED!")
    print("=" * 60)


def test_multiple_document_approvals(db_session, test_system):
    """Test approving multiple documents for same system."""
    
    org = test_system["org"]
    system = test_system["system"]
    
    print("\n📚 MULTIPLE DOCUMENTS APPROVAL TEST")
    print("=" * 60)
    
    doc_types = ["annex_iv", "soa", "instructions_for_use"]
    
    for doc_type in doc_types:
        # Submit
        submit_req = SubmitForReviewRequest(
            doc_type=doc_type,
            submitted_by=f"author-{doc_type}@test.com",
            notes=f"Submitting {doc_type}"
        )
        
        submission = submit_document_for_review(
            system_id=system.id,
            payload=submit_req,
            org=org,
            db=db_session
        )
        
        # Approve
        approve_req = ApproveDocumentRequest(
            approver_email=f"approver-{doc_type}@test.com",
            notes=f"Approved {doc_type}"
        )
        
        approved = approve_document(
            system_id=system.id,
            doc_type=doc_type,
            payload=approve_req,
            org=org,
            db=db_session
        )
        
        assert approved.status == "approved"
        print(f"✅ {doc_type}: submitted → approved")
    
    # Verify all 3 approvals exist
    all_approvals = (
        db_session.query(DocumentApproval)
        .filter(
            DocumentApproval.org_id == org.id,
            DocumentApproval.system_id == system.id
        )
        .all()
    )
    
    assert len(all_approvals) == 3
    approved_count = sum(1 for a in all_approvals if a.status == "approved")
    assert approved_count == 3
    
    print(f"\n✅ All {len(all_approvals)} documents approved")
    print("\n" + "=" * 60)
    print("🎉 MULTIPLE DOCUMENTS TEST PASSED!")
    print("=" * 60)
