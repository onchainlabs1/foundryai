from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class AISystemBase(BaseModel):
    name: str
    purpose: Optional[str] = None
    domain: Optional[str] = None
    owner_email: Optional[EmailStr] = None
    uses_biometrics: bool = False
    is_general_purpose_ai: bool = False
    impacts_fundamental_rights: bool = False
    personal_data_processed: bool = False
    training_data_sensitivity: Optional[str] = None
    output_type: Optional[str] = None
    deployment_context: Optional[str] = None
    criticality: Optional[str] = None
    notes: Optional[str] = None
    # Additional fields from frontend
    lifecycle_stage: Optional[str] = None
    affected_users: Optional[str] = None
    third_party_providers: Optional[str] = None
    risk_category: Optional[str] = None
    # New audit-grade fields
    ai_act_class: Optional[str] = None
    system_role: Optional[str] = None
    processes_sensitive_data: bool = False
    uses_gpai: bool = False
    biometrics_in_public: bool = False
    annex3_categories: Optional[str] = None
    impacted_groups: Optional[str] = None
    requires_fria: bool = False


class AISystemCreate(AISystemBase):
    model_config = ConfigDict(extra='ignore')  # Ignore extra fields from frontend


class AISystemResponse(AISystemBase):
    id: int
    org_id: int
    ai_act_class: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AssessmentResponse(BaseModel):
    ai_act_class: str  # one of: high|limited|minimal|prohibited
    is_gpai: bool
    role: str  # provider|deployer
    rationale: str
    gap: List[str]
    control_plan: List[dict]


class EvidenceCreate(BaseModel):
    label: str
    iso42001_clause: Optional[str] = None
    control_name: Optional[str] = None
    version: Optional[str] = None
    uploaded_by: Optional[str] = None
    reviewer_email: Optional[EmailStr] = None
    link_or_location: Optional[str] = None


class EvidenceResponse(BaseModel):
    id: int
    org_id: int
    system_id: Optional[int] = None
    label: str
    iso42001_clause: Optional[str] = None
    control_name: Optional[str] = None
    file_path: Optional[str] = None
    version: Optional[str] = None
    checksum: Optional[str] = None
    uploaded_by: Optional[str] = None
    upload_date: datetime
    status: str
    reviewer_email: Optional[str] = None
    link_or_location: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ReportSummary(BaseModel):
    systems: int
    high_risk: int
    # optional extended fields (may be present when implemented)
    last_30d_incidents: Optional[int] = None
    overrides_pct: Optional[float] = None
    gpai_count: Optional[int] = None
    evidence_coverage_pct: Optional[float] = None
    open_actions_7d: Optional[int] = None


class FRIACreate(BaseModel):
    applicable: bool
    answers: dict
    justification: Optional[str] = None
    # Extended fields for audit-grade compliance
    ctx_json: Optional[str] = None
    risks_json: Optional[str] = None
    safeguards_json: Optional[str] = None
    proportionality: Optional[str] = None
    residual_risk: Optional[str] = None
    review_notes: Optional[str] = None
    dpia_reference: Optional[str] = None


class FRIAResponse(BaseModel):
    id: int
    applicable: bool
    status: str
    md_url: str
    html_url: str


class ControlCreate(BaseModel):
    system_id: int
    iso_clause: str
    name: str
    priority: str
    owner_email: Optional[EmailStr] = None
    due_date: Optional[str] = None
    status: str
    rationale: Optional[str] = None
    evidence_ids: Optional[List[int]] = None  # New field for evidence linking


class ControlResponse(ControlCreate):
    id: int
    org_id: int

    model_config = ConfigDict(from_attributes=True)


class ControlBulkRequest(BaseModel):
    controls: List[ControlCreate]


class SoAItemCreate(BaseModel):
    iso_clause: str
    applicable: bool
    justification: Optional[str] = None


class IncidentCreate(BaseModel):
    system_id: int
    severity: str
    description: str
    detected_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    corrective_action: Optional[str] = None


class IncidentResponse(BaseModel):
    id: int
    org_id: int
    system_id: int
    severity: str
    description: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    corrective_action: Optional[str] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScoreResponse(BaseModel):
    org_score: float
    by_system: List[dict]
    score_unit: str = "fraction"
    tooltip: str
    coverage_pct: Optional[float] = None


# Compliance Suite Schemas
class EvidenceCitation(BaseModel):
    evidence_id: int
    page: int
    checksum: str


class DocumentParagraph(BaseModel):
    text: str
    citations: List[EvidenceCitation]


class DocumentSection(BaseModel):
    key: str
    coverage: float
    paragraphs: List[DocumentParagraph]


class ComplianceDocument(BaseModel):
    type: str
    coverage: float
    sections: List[DocumentSection]
    missing: List[str]


class ComplianceDraftRequest(BaseModel):
    system_id: Optional[int] = None
    docs: List[str] = ["annex_iv", "fria", "pmm", "soa", "risk_register"]


class ComplianceDraftResponse(BaseModel):
    docs: List[ComplianceDocument]


class RefineRequest(BaseModel):
    doc_type: str
    system_id: int
    section_key: str
    paragraphs: List[DocumentParagraph]


class RefineResponse(BaseModel):
    paragraphs: List[DocumentParagraph]
    refined_at: str

