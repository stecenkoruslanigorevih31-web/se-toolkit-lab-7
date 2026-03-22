"""
Handler for /help command.
"""


def handle_help() -> str:
    """
    Handle the /help command.

    Returns:
        Help message with available commands and natural language examples
    """
    return (
        "📖 Help - Available Commands:\n\n"
        "Slash Commands:\n"
        "/start - Start the bot and see welcome message\n"
        "/help - Show this help message\n"
        "/health - Check backend API status\n"
        "/labs - List all available labs\n"
        "/scores [lab_id] - View scores for a specific lab\n\n"
        "Natural Language Examples:\n"
        "• what labs are available?\n"
        "• show me scores for lab 4\n"
        "• which lab has the lowest pass rate?\n"
        "• who are the top 5 students in lab 4?\n"
        "• how many students are enrolled?\n"
        "• which group is best in lab 3?\n"
        "• refresh the data\n\n"
        "Just type your question in plain English!"
    )
