from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.database import get_db
from app.models import FRIA, AISystem, Organization
from app.schemas import FRIACreate, FRIAResponse
from app.services.fria import generate_fria_markdown, generate_fria_html

router = APIRouter(prefix="/systems", tags=["fria"])


@router.post("/{system_id}/fria", response_model=FRIAResponse)
def create_fria(
    system_id: int,
    payload: FRIACreate,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    system = db.query(AISystem).filter(AISystem.id == system_id, AISystem.org_id == org.id).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    md_text = generate_fria_markdown(payload.answers, payload.applicable, payload.justification)

    fria = FRIA(
        org_id=org.id,
        system_id=system_id,
        applicable=payload.applicable,
        status="submitted" if payload.applicable else "not_applicable",
        answers_json=str(payload.answers),
        summary_md=md_text,
    )
    db.add(fria)
    db.commit()
    db.refresh(fria)

    return FRIAResponse(
        id=fria.id,
        applicable=fria.applicable,
        status=fria.status,
        md_url=f"/fria/{fria.id}.md",
        html_url=f"/fria/{fria.id}.html",
    )


@router.get("/{system_id}/fria/latest", response_model=FRIAResponse)
def get_latest_fria(
    system_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    fria = (
        db.query(FRIA)
        .filter(FRIA.system_id == system_id, FRIA.org_id == org.id)
        .order_by(FRIA.created_at.desc())
        .first()
    )
    if not fria:
        raise HTTPException(status_code=404, detail="FRIA not found")
    return FRIAResponse(
        id=fria.id,
        applicable=fria.applicable,
        status=fria.status,
        md_url=f"/fria/{fria.id}.md",
        html_url=f"/fria/{fria.id}.html",
    )


# Public endpoints still require API key via verify dependency on calling routes.
static_router = APIRouter(prefix="/fria", tags=["fria"])


@static_router.get("/{fria_id}.md", response_class=PlainTextResponse)
def download_fria_md(fria_id: int, db: Session = Depends(get_db)):
    fria = db.query(FRIA).filter(FRIA.id == fria_id).first()
    if not fria:
        raise HTTPException(status_code=404, detail="FRIA not found")
    return PlainTextResponse(content=fria.summary_md or "")


@static_router.get("/{fria_id}.html", response_class=HTMLResponse)
def download_fria_html(fria_id: int, db: Session = Depends(get_db)):
    fria = db.query(FRIA).filter(FRIA.id == fria_id).first()
    if not fria:
        raise HTTPException(status_code=404, detail="FRIA not found")
    html = generate_fria_html(fria.summary_md or "")
    return HTMLResponse(content=html)


