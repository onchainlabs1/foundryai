from typing import Optional

from fastapi import Header, HTTPException, status


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Validate API key from X-API-Key header.
    
    Returns:
        Organization object if valid
        
    Raises:
        401 if API key missing (with WWW-Authenticate header)
        403 if API key invalid
    """
    from app.database import SessionLocal
    from app.models import Organization

    # Check if API key was provided
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "API-Key"},
        )

    db = SessionLocal()
    try:
        org = db.query(Organization).filter(Organization.api_key == x_api_key).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key",
            )
        return org
    finally:
        db.close()

