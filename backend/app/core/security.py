from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Organization


async def verify_api_key(
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Validate API key from X-API-Key header.
    
    Returns:
        Organization object if valid
        
    Raises:
        401 if API key missing (with WWW-Authenticate header)
        403 if API key invalid
    """
    # Check if API key was provided
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "API-Key"},
        )

    org = db.query(Organization).filter(Organization.api_key == x_api_key).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return org

