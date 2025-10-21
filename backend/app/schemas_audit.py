"""
Pydantic schemas for audit-grade onboarding.
These are additive to the existing schemas.
"""
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict


# Organization setup
class OrgSetup(BaseModel):
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[EmailStr] = None
    dpo_contact_name: Optional[str] = None
    dpo_contact_email: Optional[EmailStr] = None
    org_role: Optional[str] = None  # provider|deployer|both


# AI System setup (extends existing AISystemCreate)
class AISystemSetup(BaseModel):
    # Core fields
    name: str
    purpose: Optional[str] = None
    domain: Optional[str] = None
    owner_email: Optional[EmailStr] = None
    
    # Lifecycle & deployment
    lifecycle_stage: Optional[str] = None  # design|dev|deploy|use
    deployment_context: Optional[str] = None  # internal|public|embedded
    system_role: Optional[str] = None  # provider|deployer
    
    # Third parties & impacts
    third_party_providers: Optional[str] = None
    impacted_groups: Optional[str] = None
    affected_users: Optional[str] = None
    
    # Data & rights flags
    processes_personal_data: Optional[bool] = False
    processes_sensitive_data: Optional[bool] = False
    impacts_fundamental_rights: Optional[bool] = False
    
    # AI-specific
    uses_gpai: Optional[bool] = False
    uses_biometrics: Optional[bool] = False
    biometrics_in_public: Optional[bool] = False
    is_general_purpose_ai: Optional[bool] = False
    
    # Annex III & classification
    annex3_categories: Optional[str] = None  # JSON array as string
    ai_act_class: Optional[str] = None
    criticality: Optional[str] = None
    
    # Computed
    requires_fria: Optional[bool] = False


# Risk assessment
class RiskCreate(BaseModel):
    description: str
    likelihood: str  # L|M|H
    impact: str  # L|M|H
    mitigation: Optional[str] = None
    residual_risk: Optional[str] = None
    owner_email: Optional[EmailStr] = None
    priority: Optional[str] = "medium"  # low|med|high
    due_date: Optional[date] = None


class RiskResponse(RiskCreate):
    id: int
    org_id: int
    system_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Control (extends existing)
class ControlBulkCreate(BaseModel):
    system_id: int
    iso_clause: Optional[str] = None
    name: str
    status: Optional[str] = "missing"  # missing|partial|implemented
    owner_email: Optional[EmailStr] = None
    due_date: Optional[date] = None
    rationale: Optional[str] = None


# Oversight
class OversightCreate(BaseModel):
    oversight_mode: Optional[str] = None  # in_the_loop|on_the_loop|in_command
    intervention_rules: Optional[str] = None
    manual_override: Optional[bool] = False
    appeals_channel: Optional[str] = None
    appeals_sla_days: Optional[int] = None
    appeals_responsible_email: Optional[EmailStr] = None
    change_approval_roles: Optional[str] = None
    ethics_committee: Optional[bool] = False
    training_plan: Optional[str] = None
    comm_plan: Optional[str] = None
    external_disclosure: Optional[bool] = False


class OversightResponse(OversightCreate):
    id: int
    org_id: int
    system_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# PMM (Post-Market Monitoring)
class PMMCreate(BaseModel):
    logging_scope: Optional[str] = None
    retention_months: Optional[int] = None
    drift_threshold: Optional[str] = None
    fairness_metrics: Optional[str] = None  # JSON array as string
    incident_tool: Optional[str] = None
    audit_frequency: Optional[str] = None  # monthly|quarterly|semiannual|annual
    management_review_frequency: Optional[str] = None
    improvement_plan: Optional[str] = None
    eu_db_required: Optional[bool] = False
    eu_db_status: Optional[str] = None


class PMMResponse(PMMCreate):
    id: int
    org_id: int
    system_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Bulk operations
class RiskBulkCreate(BaseModel):
    risks: List[RiskCreate]


class ControlsBulkCreate(BaseModel):
    controls: List[ControlBulkCreate]

