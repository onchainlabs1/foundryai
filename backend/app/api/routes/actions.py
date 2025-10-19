"""
Action items management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone, date
from typing import Union

from app.core.security import verify_api_key
from app.database import get_db
from app.models import Organization, Action, AISystem, Control

router = APIRouter(prefix="/actions", tags=["actions"])


class ActionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    system_id: Optional[int] = None
    control_id: Optional[int] = None
    priority: str = "medium"  # low|medium|high|critical
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None


class ActionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None  # open|in_progress|completed|cancelled
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None


class ActionResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    assigned_to: Optional[str]
    due_date: Optional[Union[date, str]]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    system_id: Optional[int]
    control_id: Optional[int]

    model_config = {"from_attributes": True}


@router.get("/", response_model=List[ActionResponse])
async def get_actions(
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    system_id: Optional[int] = None,
):
    """Get all action items for the organization."""
    query = db.query(Action).filter(Action.org_id == org.id)
    
    if status:
        query = query.filter(Action.status == status)
    if system_id:
        query = query.filter(Action.system_id == system_id)
    
    actions = query.order_by(Action.created_at.desc()).all()
    return actions


@router.post("/", response_model=ActionResponse)
async def create_action(
    action_data: ActionCreate,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Create a new action item."""
    # Validate system_id if provided
    if action_data.system_id:
        system = db.query(AISystem).filter(
            AISystem.id == action_data.system_id,
            AISystem.org_id == org.id
        ).first()
        if not system:
            raise HTTPException(status_code=404, detail="System not found")
    
    # Validate control_id if provided
    if action_data.control_id:
        control = db.query(Control).filter(
            Control.id == action_data.control_id,
            Control.org_id == org.id
        ).first()
        if not control:
            raise HTTPException(status_code=404, detail="Control not found")
    
    # Parse due_date if provided
    due_date = None
    if action_data.due_date:
        try:
            due_date = datetime.fromisoformat(action_data.due_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due_date format")
    
    action = Action(
        org_id=org.id,
        title=action_data.title,
        description=action_data.description,
        system_id=action_data.system_id,
        control_id=action_data.control_id,
        priority=action_data.priority,
        assigned_to=action_data.assigned_to,
        due_date=due_date,
        status="open"
    )
    
    db.add(action)
    db.commit()
    db.refresh(action)
    
    return action


@router.get("/{action_id}", response_model=ActionResponse)
async def get_action(
    action_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Get a specific action item."""
    action = db.query(Action).filter(
        Action.id == action_id,
        Action.org_id == org.id
    ).first()
    
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    return action


@router.patch("/{action_id}", response_model=ActionResponse)
async def update_action(
    action_id: int,
    action_data: ActionUpdate,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Update an action item."""
    action = db.query(Action).filter(
        Action.id == action_id,
        Action.org_id == org.id
    ).first()
    
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    # Update fields
    update_data = action_data.model_dump(exclude_unset=True)
    
    # Handle due_date parsing
    if 'due_date' in update_data and update_data['due_date']:
        try:
            update_data['due_date'] = datetime.fromisoformat(update_data['due_date'].replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due_date format")
    
    # Handle status change to completed
    if 'status' in update_data and update_data['status'] == 'completed':
        update_data['completed_at'] = datetime.now(timezone.utc)
    elif 'status' in update_data and update_data['status'] != 'completed':
        update_data['completed_at'] = None
    
    # Update the action
    for field, value in update_data.items():
        setattr(action, field, value)
    
    action.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(action)
    
    return action


@router.delete("/{action_id}")
async def delete_action(
    action_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Delete an action item."""
    action = db.query(Action).filter(
        Action.id == action_id,
        Action.org_id == org.id
    ).first()
    
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    db.delete(action)
    db.commit()
    
    return {"message": "Action deleted successfully"}
