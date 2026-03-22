"""
Handler for /start command.

This handler is independent of Telegram - it just returns a welcome message.
"""


def handle_start() -> str:
    """
    Handle the /start command.

    Returns:
        Welcome message for new users
    """
    return (
        "👋 Welcome to the LMS Bot!\n\n"
        "I can help you check your lab scores, submissions, and analytics.\n\n"
        "You can use slash commands like /help, /labs, /health, /scores\n"
        "Or just ask me questions in plain English:\n"
        "• what labs are available?\n"
        "• show me scores for lab 4\n"
        "• which lab has the lowest pass rate?\n\n"
        "Use /help to see all commands and examples."
    )
