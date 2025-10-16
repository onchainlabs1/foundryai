from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import relationship

from app.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

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

    organization = relationship("Organization", back_populates="systems")
    evidence = relationship("Evidence", back_populates="system")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    system_id = Column(Integer, ForeignKey("ai_systems.id"), nullable=True)
    label = Column(String(255), nullable=False)
    iso42001_clause = Column(String(100))
    control_name = Column(String(255))
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
    severity = Column(String(20), default="low")
    description = Column(Text)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)
    corrective_action = Column(Text)
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


# Helpful composite indexes
Index("ix_fria_org_system", FRIA.org_id, FRIA.system_id)
Index("ix_controls_org_system", Control.org_id, Control.system_id)
Index("ix_soa_org_system", SoAItem.org_id, SoAItem.system_id)
Index("ix_incidents_org_system", Incident.org_id, Incident.system_id)

