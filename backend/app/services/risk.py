def classify_ai_act(system_data: dict) -> str:
    """
    Classify AI system according to EU AI Act risk levels.

    Args:
        system_data: Dictionary with system attributes

    Returns:
        Risk classification: one of {"high", "limited", "minimal", "prohibited"}
    """
    if system_data.get("uses_biometrics") and system_data.get("deployment_context") == "public":
        return "high"
    if system_data.get("impacts_fundamental_rights"):
        return "high"
    # GPAI is tracked separately via is_gpai; classification remains in 4-class set
    if system_data.get("is_general_purpose_ai"):
        return "limited"
    return "minimal"


def detect_role(system_data: dict) -> str:
    """Heuristic for role detection (provider|deployer).

    - internal deployments → deployer
    - presence of training/data sensitivity hints → provider
    - default provider
    """
    if system_data.get("deployment_context") == "internal":
        return "deployer"
    if system_data.get("training_data_sensitivity"):
        return "provider"
    return "provider"


def is_gpai(system_data: dict) -> bool:
    """Determine if considered General Purpose AI (GPAI) for dashboards."""
    return bool(system_data.get("is_general_purpose_ai"))

