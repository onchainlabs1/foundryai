"""
FRIA (Fundamental Rights Impact Assessment) logic.
Determines when FRIA is required based on EU AI Act criteria.
"""
import json
from typing import Optional


HIGH_RISK_ANNEX3_CATEGORIES = {
    "biometrics",
    "critical_infrastructure",
    "education",
    "employment",
    "essential_services",
    "law_enforcement",
    "migration",
    "justice",
    "democratic_process"
}


def compute_requires_fria(
    impacts_fundamental_rights: bool = False,
    biometrics_in_public: bool = False,
    annex3_categories: Optional[str] = None
) -> bool:
    """
    Determine if FRIA is required for an AI system.
    
    FRIA is required if:
    1. System impacts fundamental rights, OR
    2. Uses biometrics in public spaces, OR
    3. Falls under high-risk Annex III categories
    
    Args:
        impacts_fundamental_rights: Boolean flag
        biometrics_in_public: Boolean flag
        annex3_categories: JSON string of categories (e.g., '["biometrics", "employment"]')
    
    Returns:
        True if FRIA is required, False otherwise
    """
    
    # Check explicit flags
    if impacts_fundamental_rights:
        return True
    
    if biometrics_in_public:
        return True
    
    # Check Annex III categories
    if annex3_categories:
        try:
            categories = json.loads(annex3_categories)
            if isinstance(categories, list):
                # Check if any category is high-risk
                for category in categories:
                    if category.lower() in HIGH_RISK_ANNEX3_CATEGORIES:
                        return True
        except (json.JSONDecodeError, TypeError):
            # If annex3_categories is not JSON, treat as comma-separated string
            if isinstance(annex3_categories, str):
                categories_list = [c.strip().lower() for c in annex3_categories.split(',')]
                for category in categories_list:
                    if category in HIGH_RISK_ANNEX3_CATEGORIES:
                        return True
    
    return False

