"""
Handler for /scores command.
"""


def handle_scores(lab_id: str | None = None) -> str:
    """
    Handle the /scores command.
    
    Args:
        lab_id: Optional lab identifier (e.g., "lab-04")
    
    Returns:
        Score information (placeholder for now)
    """
    if lab_id:
        return f"📊 Scores for {lab_id}:\n\nYour score: -- (placeholder)\n\nReal implementation coming in Task 2."
    else:
        return (
            "📊 Scores:\n\n"
            "Usage: /scores <lab_id>\n\n"
            "Examples:\n"
            "/scores lab-04\n"
            "/scores lab-03\n\n"
            "Real implementation coming in Task 2."
        )
