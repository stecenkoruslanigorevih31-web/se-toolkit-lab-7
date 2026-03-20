#!/usr/bin/env python3
"""
Telegram bot entry point with --test mode.

Usage:
    uv run bot.py --test "/start"    # Test mode, prints response to stdout
    uv run bot.py                    # Production mode, connects to Telegram
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
        metavar="COMMAND",
        help="Test mode: run a command and print response to stdout",
    )
    args = parser.parse_args()

    if args.test:
        # Test mode: call handler directly and print result
        command = args.test.strip()
        response = handle_command(command)
        print(response)
        sys.exit(0)

    # Production mode: start Telegram bot
    logger.info("Starting Telegram bot in production mode...")
    run_telegram_bot()


def handle_command(command: str) -> str:
    """
    Route a command to the appropriate handler.
    
    Args:
        command: The command string (e.g., "/start", "/help", "/scores lab-04")
    
    Returns:
        Response text to send to the user
    """
    parts = command.strip().split(maxsplit=1)
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
        return f"Command '{cmd}' not implemented yet"


def run_telegram_bot():
    """
    Start the Telegram bot and listen for messages.
    
    Loads BOT_TOKEN from config and registers command handlers.
    """
    try:
        from telegram import Update
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
        await update.message.reply_text(response)

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

    # Build application
    application = Application.builder().token(config.bot_token).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("health", health_command))
    application.add_handler(CommandHandler("labs", labs_command))
    application.add_handler(CommandHandler("scores", scores_command))
    application.add_handler(CommandHandler("unknown", unknown_command))

    # Start the bot
    logger.info("Bot is running... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
