from typing import List

from app.mappers.iso42001_ai_act import ISO_TO_AI_ACT


def generate_gap(ai_act_class: str, current_controls: List[str] = None) -> List[str]:
    """
    Generate ISO 42001 gap analysis.

    Args:
        ai_act_class: AI Act risk classification
        current_controls: List of currently implemented controls

    Returns:
        List of missing ISO 42001 clauses
    """
    if current_controls is None:
        current_controls = []

    # All required ISO clauses
    all_clauses = list(ISO_TO_AI_ACT.keys())

    # Simple set difference
    missing = [clause for clause in all_clauses if clause not in current_controls]

    return missing


def generate_control_plan(ai_act_class: str) -> List[dict]:
    """
    Generate RACI control plan stub.

    Args:
        ai_act_class: AI Act risk classification

    Returns:
        List of control items with RACI placeholders
    """
    controls = []
    for iso_clause, ai_act_requirements in ISO_TO_AI_ACT.items():
        controls.append(
            {
                "iso_clause": iso_clause,
                "ai_act_requirements": ai_act_requirements,
                "responsible": "TBD",
                "accountable": "TBD",
                "consulted": "TBD",
                "informed": "TBD",
            }
        )
    return controls

