from datetime import datetime, timezone
from typing import Dict

import markdown as md


def generate_fria_markdown(answers: Dict, applicable: bool, justification: str | None = None) -> str:
    """Render a simple FRIA markdown summary from answers.

    This MVP version enumerates 10 questions and includes applicability and optional justification.
    """
    lines = ["# Fundamental Rights Impact Assessment (FRIA)", "", f"Applicable: {'Yes' if applicable else 'No'}"]
    if justification:
        lines += ["", "Justification:", justification]
    lines += ["", "## Answers"]
    for key, value in answers.items():
        lines.append(f"- {key}: {value}")
    lines += ["", f"Generated at: {datetime.now(timezone.utc).isoformat()}"]
    return "\n".join(lines)


def generate_fria_html(markdown_text: str) -> str:
    """Convert markdown to HTML for quick preview/download."""
    return md.markdown(markdown_text)


