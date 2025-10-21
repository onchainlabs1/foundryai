"""
Audit Logger Service
Tracks data sources, calculations, and changes for compliance and debugging
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.models import Organization

# Configure audit logger
audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)

# Create file handler for audit logs
audit_handler = logging.FileHandler('audit.log')
audit_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
audit_handler.setFormatter(formatter)

# Add handler to logger
audit_logger.addHandler(audit_handler)


class AuditLogger:
    """Service for logging data operations and calculations"""
    
    @staticmethod
    def log_data_access(
        endpoint: str,
        org_id: int,
        data_type: str,
        record_count: int,
        calculation_details: Optional[Dict[str, Any]] = None
    ):
        """Log data access operations"""
        log_entry = {
            "event_type": "data_access",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "endpoint": endpoint,
            "org_id": org_id,
            "data_type": data_type,
            "record_count": record_count,
            "calculation_details": calculation_details or {}
        }
        
        audit_logger.info(f"DATA_ACCESS: {json.dumps(log_entry)}")
    
    @staticmethod
    def log_calculation(
        calculation_type: str,
        org_id: int,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        formula: Optional[str] = None
    ):
        """Log calculation operations"""
        log_entry = {
            "event_type": "calculation",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "calculation_type": calculation_type,
            "org_id": org_id,
            "inputs": inputs,
            "outputs": outputs,
            "formula": formula
        }
        
        audit_logger.info(f"CALCULATION: {json.dumps(log_entry)}")
    
    @staticmethod
    def log_data_validation(
        data_type: str,
        org_id: int,
        validation_result: Dict[str, Any],
        errors: List[str],
        warnings: List[str]
    ):
        """Log data validation results"""
        log_entry = {
            "event_type": "data_validation",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_type": data_type,
            "org_id": org_id,
            "validation_result": validation_result,
            "errors": errors,
            "warnings": warnings
        }
        
        audit_logger.info(f"DATA_VALIDATION: {json.dumps(log_entry)}")
    
    @staticmethod
    def log_dummy_data_detection(
        endpoint: str,
        org_id: int,
        detected_patterns: List[str],
        action_taken: str
    ):
        """Log detection of dummy/hardcoded data"""
        log_entry = {
            "event_type": "dummy_data_detection",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "endpoint": endpoint,
            "org_id": org_id,
            "detected_patterns": detected_patterns,
            "action_taken": action_taken
        }
        
        audit_logger.warning(f"DUMMY_DATA_DETECTED: {json.dumps(log_entry)}")
    
    @staticmethod
    def log_data_source(
        data_type: str,
        org_id: int,
        source: str,
        confidence: str,
        last_updated: str
    ):
        """Log data source information"""
        log_entry = {
            "event_type": "data_source",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_type": data_type,
            "org_id": org_id,
            "source": source,
            "confidence": confidence,
            "last_updated": last_updated
        }
        
        audit_logger.info(f"DATA_SOURCE: {json.dumps(log_entry)}")


def audit_data_access(func):
    """Decorator to automatically log data access operations"""
    def wrapper(*args, **kwargs):
        # Extract org from arguments if available
        org = None
        for arg in args:
            if isinstance(arg, Organization):
                org = arg
                break
        
        # Extract db from arguments if available
        db = None
        for arg in args:
            if hasattr(arg, 'query'):  # SQLAlchemy session
                db = arg
                break
        
        # Call original function
        result = func(*args, **kwargs)
        
        # Log the operation
        if org and db:
            AuditLogger.log_data_access(
                endpoint=func.__name__,
                org_id=org.id,
                data_type=type(result).__name__,
                record_count=len(result) if isinstance(result, (list, dict)) else 1
            )
        
        return result
    
    return wrapper


def audit_calculation(calculation_type: str, formula: Optional[str] = None):
    """Decorator to automatically log calculation operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract org from arguments if available
            org = None
            for arg in args:
                if isinstance(arg, Organization):
                    org = arg
                    break
            
            # Call original function
            result = func(*args, **kwargs)
            
            # Log the calculation
            if org:
                AuditLogger.log_calculation(
                    calculation_type=calculation_type,
                    org_id=org.id,
                    inputs=kwargs,
                    outputs=result if isinstance(result, dict) else {"result": result},
                    formula=formula
                )
            
            return result
        
        return wrapper
    return decorator


# Example usage in reports.py:
"""
@audit_calculation("compliance_score", "0.6*implemented + 0.4*coverage")
def get_score(org: Organization, db: Session):
    # ... calculation logic
    return result

@audit_data_access
def get_summary(org: Organization, db: Session):
    # ... data access logic
    return result
"""
