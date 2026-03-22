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
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show help message\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores - View your scores"
    )
