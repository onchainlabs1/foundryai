"""
Custom SQLAlchemy types for AIMS Readiness platform.
"""
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, TypeDecorator


class UTCDateTime(TypeDecorator):
    """
    A DateTime type that ensures all datetime values are timezone-aware UTC.
    
    This is particularly important for SQLite, which doesn't preserve timezone
    information by default. This decorator ensures that:
    - All datetime values are stored as UTC
    - All datetime values are returned as timezone-aware UTC
    - Naive datetimes are assumed to be UTC
    """
    
    impl = DateTime
    cache_ok = True
    
    def process_bind_param(self, value: Any, dialect) -> Any:
        """Process value when storing to database."""
        if value is None:
            return None
            
        if isinstance(value, datetime):
            # If naive, assume UTC
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            # Convert to UTC
            return value.astimezone(timezone.utc)
            
        return value
    
    def process_result_value(self, value: Any, dialect) -> Any:
        """Process value when reading from database."""
        if value is None:
            return None
            
        if isinstance(value, datetime):
            # If naive, assume UTC
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            # Ensure it's UTC
            return value.astimezone(timezone.utc)
            
        return value
