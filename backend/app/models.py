from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # New audit-grade fields
    primary_contact_name = Column(String(255))
    primary_contact_email = Column(String(255))
    dpo_contact_name = Column(String(255))
    dpo_contact_email = Column(String(255))
    org_role = Column(String(50))  # provider|deployer|both

    systems = relationship("AISystem", back_populates="organization")
    evidence = relationship("Evidence", back_populates="organization")


class AISystem(Base):
    __tablename__ = "ai_systems"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    purpose = Column(Text)
    domain = Column(String(255))
    owner_email = Column(String(255))
    uses_biometrics = Column(Boolean, default=False)
    is_general_purpose_ai = Column(Boolean, default=False)
    impacts_fundamental_rights = Column(Boolean, default=False)
    personal_data_processed = Column(Boolean, default=False)
    training_data_sensitivity = Column(String(50))
    output_type = Column(String(100))
    deployment_context = Column(String(100))
    criticality = Column(String(50))
    notes = Column(Text)
    ai_act_class = Column(String(50))
    # Additional fields from frontend
    lifecycle_stage = Column(String(100))
    affected_users = Column(Text)
    third_party_providers = Column(Text)
    risk_category = Column(String(255))
    
    # New audit-grade fields for EU AI Act + ISO/IEC 42001
    system_role = Column(String(50))  # provider|deployer
    processes_sensitive_data = Column(Boolean, default=False)
    uses_gpai = Column(Boolean, default=False)
    biometrics_in_public = Column(Boolean, default=False)
    annex3_categories = Column(Text)  # JSON array of categories
    impacted_groups = Column(Text)  # Comma-separated or JSON
    requires_fria = Column(Boolean, default=False)  # Computed flag
    eu_db_status = Column(String(50), default='pending')  # pending|registered|n/a
    dpia_link = Column(String(500))  # URL or reference to GDPR Art. 35 DPIA
    
    @property
    def requires_fria_computed(self) -> bool:
        """Compute if system requires FRIA based on EU AI Act criteria."""
        return (
            self.impacts_fundamental_rights or
            self.uses_biometrics or
            self.biometrics_in_public or
            self.ai_act_class == 'high-risk'
        )
    
    @property
    def eu_db_required_computed(self) -> bool:
        """Compute if system requires EU Database registration."""
        # Provider role is determined by:
        # 1. system_role field if set, OR
        # 2. organization org_role
        is_provider = (
            (self.system_role == 'provider') or
            (self.organization and self.organization.org_role == 'provider')
        )
        return is_provider and self.ai_act_class == 'high-risk'

    organization = relationship("Organization", back_populates="systems")
    evidence = relationship("Evidence", back_populates="system")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    system_id = Column(Integer, ForeignKey("ai_systems.id"), nullable=True)
    control_id = Column(Integer, ForeignKey("controls.id"), nullable=True)  # New field
    label = Column(String(255), nullable=False)
    iso42001_clause = Column(String(100))
    control_name = Column(String(255))  # Keep for backward compatibility
    file_path = Column(String(500))
    version = Column(String(50))
    checksum = Column(String(64))
    uploaded_by = Column(String(255))
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="uploaded")
    reviewer_email = Column(String(255))
    link_or_location = Column(String(500))

    organization = relationship("Organization", back_populates="evidence")
    system = relationship("AISystem", back_populates="evidence")
    control = relationship("Control")  # New relationship


# --- New additive models (do not modify existing ones) ---


class FRIA(Base):
    __tablename__ = "fria"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), index=True, nullable=False)
    system_id = Column(Integer, ForeignKey("ai_systems.id"), index=True, nullable=False)
    applicable = Column(Boolean, default=True)
    status = Column(String(50), default="draft")
    answers_json = Column(Text)
    summary_md = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Extended FRIA fields for audit-grade compliance
    ctx_json = Column(Text)  # System context snapshot
    risks_json = Column(Text)  # Identified risks
    safeguards_json = Column(Text)  # Mitigation measures
    proportionality = Column(Text)  # Proportionality analysis
    residual_risk = Column(String(50))  # low/medium/high
    review_notes = Column(Text)  # Reviewer comments
    dpia_reference = Column(String(500))  # Link to existing DPIA if applicable


class Control(Base):
    __tablename__ = "controls"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), index=True, nullable=False)
    system_id = Column(Integer, ForeignKey("ai_systems.id"), index=True, nullable=False)
    iso_clause = Column(String(100), index=True)
    name = Column(String(255), nullable=False)
    priority = Column(String(20), default="medium")
    status = Column(String(20), default="missing")  # missing|partial|implemented
    owner_email = Column(String(255))
    due_date = Column(Date, nullable=True)
    rationale = Column(Text)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SoAItem(Base):
    __tablename__ = "soa_items"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), index=True, nullable=False)
    system_id = Column(Integer, ForeignKey("ai_systems.id"), index=True, nullable=False)
    iso_clause = Column(String(100), index=True)
    applicable = Column(Boolean, default=True)
    justification = Column(Text)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), index=True, nullable=False)
    system_id = Column(Integer, ForeignKey("ai_systems.id"), index=True, nullable=False)
    severity = Column(String(20), default="low")  # low|medium|high
    description = Column(Text)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)
    corrective_action = Column(Text)
    notify_list = Column(Text)  # Comma-separated emails or JSON
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ArtifactText(Base):
    """Evidence vault for storing text snippets from uploaded documents."""
    __tablename__ = "artifact_text"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), index=True, nullable=False)
    system_id = Column(Integer, ForeignKey("ai_systems.id"), index=True, nullable=False)
    evidence_id = Column(Integer, ForeignKey("evidence.id"), index=True, nullable=False)
    file_path = Column(String(512), nullable=False)
    page = Column(Integer, nullable=False, default=1)
    checksum = Column(String(64), nullable=False)  # SHA-256 of the text content
    iso_clause = Column(String(100), index=True, nullable=True)  # e.g., "ISO42001:6.1.1"
    ai_act_ref = Column(String(100), nullable=True)  # e.g., "Art12", "AnnexIV.8.3"
    lang = Column(String(10), nullable=True, default="en")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    organization = relationship("Organization")
    ai_system = relationship("AISystem")
    evidence = relationship("Evidence")

    # Index for full-text search
    __table_args__ = (
        Index('idx_artifact_text_search', 'org_id', 'system_id', 'content'),
        Index('idx_artifact_iso_clause', 'org_id', 'iso_clause'),
        Index('idx_artifact_ai_act', 'org_id', 'ai_act_ref'),
    )


class Action(Base):
    """Action items for compliance tracking."""
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), index=True, nullable=False)
    system_id = Column(Integer, ForeignKey("ai_systems.id"), index=True, nullable=True)
    control_id = Column(Integer, ForeignKey("controls.id"), index=True, nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="open")  # open|in_progress|completed|cancelled
    priority = Column(String(20), default="medium")  # low|medium|high|critical
    assigned_to = Column(String(255))
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    organization = relationship("Organization")
    ai_system = relationship("AISystem")
    control = relationship("Control")


# Helpful composite indexes
Index("ix_fria_org_system", FRIA.org_id, FRIA.system_id)
Index("ix_controls_org_system", Control.org_id, Control.system_id)
Index("ix_soa_org_system", SoAItem.org_id, SoAItem.system_id)
Index("ix_incidents_org_system", Incident.org_id, Incident.system_id)


class OnboardingData(Base):
    """Store onboarding data for document generation"""
    __tablename__ = "onboarding_data"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), index=True, nullable=False)
    system_id = Column(Integer, ForeignKey("ai_systems.id"), index=True, nullable=False)
    data_json = Column(Text, nullable=False)  # JSON string with onboarding data
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    organization = relationship("Organization")
    system = relationship("AISystem")


class AIRisk(Base):
    """Risk assessment for AI systems"""
    __tablename__ = "ai_risk"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), index=True, nullable=False)
    system_id = Column(Integer, ForeignKey("ai_systems.id"), index=True, nullable=False)
    description = Column(Text, nullable=False)
    likelihood = Column(String(10))  # L|M|H
    impact = Column(String(10))  # L|M|H
    mitigation = Column(Text)
    residual_risk = Column(String(255))
    owner_email = Column(String(255))
    priority = Column(String(20), default="medium")  # low|med|high
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    organization = relationship("Organization")
    ai_system = relationship("AISystem")


class Oversight(Base):
    """Human oversight configuration for AI systems"""
    __tablename__ = "oversight"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), index=True, nullable=False)
    system_id = Column(Integer, ForeignKey("ai_systems.id"), index=True, nullable=False)
    oversight_mode = Column(String(50))  # in_the_loop|on_the_loop|in_command
    intervention_rules = Column(Text)
    manual_override = Column(Boolean, default=False)
    appeals_channel = Column(String(500))  # URL or email
    appeals_sla_days = Column(Integer)
    appeals_responsible_email = Column(String(255))
    change_approval_roles = Column(Text)  # JSON array or comma-separated
    ethics_committee = Column(Boolean, default=False)
    training_plan = Column(Text)
    comm_plan = Column(Text)
    external_disclosure = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    organization = relationship("Organization")
    ai_system = relationship("AISystem")


class PMM(Base):
    """Post-Market Monitoring (Art. 72) configuration"""
    __tablename__ = "pmm"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), index=True, nullable=False)
    system_id = Column(Integer, ForeignKey("ai_systems.id"), index=True, nullable=False)
    logging_scope = Column(Text)
    retention_months = Column(Integer)
    drift_threshold = Column(String(50))  # e.g., "0.1" or "10%"
    fairness_metrics = Column(Text)  # JSON array
    incident_tool = Column(String(255))
    audit_frequency = Column(String(50))  # monthly|quarterly|semiannual|annual
    management_review_frequency = Column(String(50))  # quarterly|semiannual|annual
    improvement_plan = Column(Text)
    eu_db_required = Column(Boolean, default=False)
    eu_db_status = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    organization = relationship("Organization")
    ai_system = relationship("AISystem")


class ModelVersion(Base):
    """Model version tracking for change management."""
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), index=True, nullable=False)
    system_id = Column(Integer, ForeignKey("ai_systems.id"), index=True, nullable=False)
    version = Column(String(50), nullable=False)  # e.g., "1.0.0", "2.1.3"
    released_at = Column(DateTime, nullable=False)
    approver_email = Column(String(255))
    notes = Column(Text)
    artifact_hash = Column(String(64))  # SHA-256 of model artifact
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    organization = relationship("Organization")
    ai_system = relationship("AISystem")


class DocumentApproval(Base):
    """Document approval tracking for audit trail."""
    __tablename__ = "doc_approvals"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), index=True, nullable=False)
    system_id = Column(Integer, ForeignKey("ai_systems.id"), index=True, nullable=False)
    doc_type = Column(String(100), nullable=False)  # annex_iv|fria|soa|pmm|instructions_for_use
    status = Column(String(50), default="draft")  # draft|submitted|approved|rejected
    submitted_by = Column(String(255))
    submitted_at = Column(DateTime, nullable=True)
    approver_email = Column(String(255))
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text)
    notes = Column(Text)
    document_hash = Column(String(64))  # SHA-256 of approved document version
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    organization = relationship("Organization")
    ai_system = relationship("AISystem")


# Additional indexes for new tables
Index("ix_ai_risk_org_system", AIRisk.org_id, AIRisk.system_id)
Index("ix_oversight_org_system", Oversight.org_id, Oversight.system_id)
Index("ix_pmm_org_system", PMM.org_id, PMM.system_id)
Index("ix_model_versions_org_system", ModelVersion.org_id, ModelVersion.system_id)
Index("ix_doc_approvals_org_system", DocumentApproval.org_id, DocumentApproval.system_id)
Index("ix_doc_approvals_doc_type", DocumentApproval.org_id, DocumentApproval.system_id, DocumentApproval.doc_type)

