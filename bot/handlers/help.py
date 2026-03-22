"""
Handler for /help command.
"""


def handle_help() -> str:
    """
    Handle the /help command.
    
    Returns:
        Help message with available commands
    """
    return (
        "📖 Help - Available Commands:\n\n"
        "/start - Start the bot and see welcome message\n"
        "/help - Show this help message\n"
        "/health - Check backend API status\n"
        "/labs - List all available labs\n"
        "/scores [lab_id] - View your scores for a specific lab\n\n"
        "Examples:\n"
        "/scores lab-04\n"
        "/labs"
    )
