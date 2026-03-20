#!/usr/bin/env python3
"""
Telegram bot entry point with --test mode.

Usage:
    uv run bot.py --test "/start"    # Test mode, prints response to stdout
    uv run bot.py                    # Production mode, connects to Telegram
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from handlers.start import handle_start
from handlers.help import handle_help
from handlers.health import handle_health
from handlers.labs import handle_labs
from handlers.scores import handle_scores


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
    print("Starting Telegram bot (production mode not implemented yet)")
    print("Use --test mode for now: uv run bot.py --test '/start'")


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


if __name__ == "__main__":
    main()
