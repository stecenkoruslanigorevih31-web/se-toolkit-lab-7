#!/usr/bin/env python3
"""
Telegram bot entry point with --test mode.

Usage:
    uv run bot.py --test "/start"           # Test mode: slash command
    uv run bot.py --test "show labs"        # Test mode: natural language
    uv run bot.py                           # Production mode: connects to Telegram
"""

import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from handlers.start import handle_start
from handlers.help import handle_help
from handlers.health import handle_health
from handlers.labs import handle_labs
from handlers.scores import handle_scores
from handlers.intent_router import handle_natural_language
from config import load_config

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="MESSAGE",
        help="Test mode: run a command or natural language query and print response to stdout",
    )
    args = parser.parse_args()

    if args.test:
        # Test mode: route to appropriate handler and print result
        message = args.test.strip()
        response = handle_message(message)
        print(response)
        sys.exit(0)

    # Production mode: start Telegram bot
    logger.info("Starting Telegram bot in production mode...")
    run_telegram_bot()


def handle_message(message: str) -> str:
    """
    Route a message to the appropriate handler.

    Slash commands (/start, /help, etc.) go to command handlers.
    Everything else goes to the LLM intent router.

    Args:
        message: The message string (e.g., "/start", "show labs", "which lab is hardest?")

    Returns:
        Response text to send to the user
    """
    message = message.strip()

    # Check if it's a slash command
    if message.startswith("/"):
        parts = message.split(maxsplit=1)
        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else None

        if cmd == "/start":
            return handle_start()
        elif cmd == "/help":
            return handle_help()
        elif cmd == "/health":
            return handle_health()
        elif cmd == "/labs":
            return handle_labs()
        elif cmd == "/scores":
            return handle_scores(arg)
        else:
            return f"Command '{cmd}' not implemented. Use /help to see available commands."
    else:
        # Natural language query - use LLM router
        return handle_natural_language(message)


def run_telegram_bot():
    """
    Start the Telegram bot and listen for messages.

    Loads BOT_TOKEN from config and registers command handlers.
    Also handles plain text messages via the intent router.
    """
    try:
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
        from telegram.ext import (
            Application,
            CommandHandler,
            ContextTypes,
            MessageHandler,
            filters,
        )
    except ImportError:
        logger.error(
            "python-telegram-bot not installed. Run: uv add python-telegram-bot"
        )
        sys.exit(1)

    config = load_config()

    if not config.bot_token:
        logger.error("BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)

    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = handle_start()
        # Add inline keyboard buttons
        keyboard = [
            [
                InlineKeyboardButton("📚 Labs", callback_data="labs"),
                InlineKeyboardButton("🏥 Health", callback_data="health"),
            ],
            [
                InlineKeyboardButton("📊 Scores", callback_data="scores"),
                InlineKeyboardButton("❓ Help", callback_data="help"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(response, reply_markup=reply_markup)

    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = handle_help()
        await update.message.reply_text(response)

    async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = handle_health()
        await update.message.reply_text(response)

    async def labs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = handle_labs()
        await update.message.reply_text(response)

    async def scores_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        lab_id = context.args[0] if context.args else None
        response = handle_scores(lab_id)
        await update.message.reply_text(response)

    async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = f"Sorry, I don't understand that command. Use /help to see available commands."
        await update.message.reply_text(response)

    async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle plain text messages using the LLM intent router."""
        user_message = update.message.text
        logger.info(f"Received message: {user_message}")

        try:
            response = handle_natural_language(user_message)
            await update.message.reply_text(response)
        except Exception as e:
            logger.exception("Error handling text message")
            await update.message.reply_text(
                f"Sorry, I encountered an error: {e}. Please try again."
            )

    async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button callbacks."""
        query = update.callback_query
        await query.answer()

        data = query.data

        if data == "labs":
            response = handle_labs()
        elif data == "health":
            response = handle_health()
        elif data == "scores":
            response = handle_scores(None)
        elif data == "help":
            response = handle_help()
        else:
            response = "Unknown action."

        await query.edit_message_text(response)

    # Build application
    application = Application.builder().token(config.bot_token).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("health", health_command))
    application.add_handler(CommandHandler("labs", labs_command))
    application.add_handler(CommandHandler("scores", scores_command))
    application.add_handler(CommandHandler("unknown", unknown_command))

    # Register callback query handler for inline buttons
    application.add_handler(
        MessageHandler(filters.Regex("^(labs|health|scores|help)$"), button_callback)
    )

    # Register message handler for plain text (must be last)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    # Start the bot
    logger.info("Bot is running... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
