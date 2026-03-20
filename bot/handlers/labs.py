"""
Handler for /labs command.
"""


def handle_labs() -> str:
    """
    Handle the /labs command.
    
    Returns:
        List of available labs (placeholder for now)
    """
    return (
        "📚 Available Labs:\n\n"
        "lab-01 - Introduction\n"
        "lab-02 - Setup\n"
        "lab-03 - Basic Features\n"
        "lab-04 - Advanced Features\n\n"
        "Use /scores <lab_id> to view your score for a specific lab."
    )
