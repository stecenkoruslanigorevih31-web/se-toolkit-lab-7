# Development Plan — LMS Telegram Bot

## Overview

This document outlines the implementation plan for the LMS Telegram Bot across all four tasks. The bot provides students with access to their lab scores, submissions, and analytics through a Telegram interface, with intelligent intent routing using an LLM.

## Architecture

The bot follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│         Telegram Bot (bot.py)           │  ← Transport layer
├─────────────────────────────────────────┤
│         Intent Router (handlers/)       │  ← Command routing
├─────────────────────────────────────────┤
│         Handlers (handlers/)            │  ← Business logic
├─────────────────────────────────────────┤
│    Services (services/)                 │  ← External APIs
│    - LMS API Client                     │
│    - LLM Client                         │
└─────────────────────────────────────────┘
```

**Key design principle:** Handlers are pure functions that take input and return text. They don't depend on Telegram — the same logic works from `--test` mode, unit tests, or the actual Telegram bot.

---

## Task 1: Plan and Scaffold

**Goal:** Create project structure and development plan.

**Deliverables:**

- `bot/` directory with entry point, handlers, config
- `--test` mode for offline verification
- `PLAN.md` (this document)

**Approach:**

1. Create `bot.py` with argparse for `--test` flag
2. Create `handlers/` directory with placeholder handlers
3. Create `config.py` for environment variable loading
4. Create `pyproject.toml` with dependencies
5. Test all commands in `--test` mode

**Status:** ✅ Complete

---

## Task 2: Backend Integration

**Goal:** Connect handlers to the LMS backend API.

**Deliverables:**

- `services/lms_client.py` — HTTP client for LMS API
- Updated handlers that fetch real data
- Error handling for API failures

**Approach:**

1. Create `LMSClient` class using `httpx`
2. Implement Bearer token authentication
3. Add methods: `get_health()`, `get_labs()`, `get_scores(lab_id)`
4. Update handlers to call the client
5. Handle errors gracefully (timeouts, 401, 500)

**Key considerations:**

- API URL and key from environment variables
- Timeout handling (backend may be slow)
- User-friendly error messages

---

## Task 3: Intent Routing with LLM

**Goal:** Enable natural language queries using an LLM.

**Deliverables:**

- `services/llm_client.py` — LLM API client
- `handlers/intent_router.py` — LLM-based routing
- Tool descriptions for the LLM

**Approach:**

1. Create `LLMClient` class for Qwen Code API
2. Define tools with clear descriptions:
   - `get_scores(lab_id)` — fetch scores for a lab
   - `list_labs()` — list all available labs
   - `check_health()` — check backend status
3. Use function calling pattern: LLM decides which tool to call
4. Route natural language to tools, then format response

**Example flow:**

```
User: "what labs are available"
  → Intent Router
    → LLM analyzes: "user wants list of labs"
    → Calls: list_labs()
    → Returns: formatted lab list
```

**Key considerations:**

- Tool descriptions must be clear and specific
- Don't use regex for routing — let the LLM decide
- Fallback only when LLM service is unreachable

---

## Task 4: Deployment

**Goal:** Deploy the bot on the VM and integrate with Telegram.

**Deliverables:**

- Production-ready `bot.py` with Telegram connection
- `.env.bot.secret` on VM with all credentials
- Bot running as a background service

**Approach:**

1. Add Telegram bot client using `python-telegram-bot`
2. Load `BOT_TOKEN` from environment
3. Register command handlers with Telegram
4. Deploy to VM and test in real Telegram

**Deployment steps:**

1. Pull latest code on VM
2. Run `uv sync` in `bot/`
3. Start bot: `nohup uv run bot.py > bot.log 2>&1 &`
4. Test in Telegram with `/start`, `/help`, etc.

---

## Testing Strategy

**Test mode (`--test`):**

- All commands work without Telegram connection
- Prints response to stdout, exits with code 0
- Used by autochecker for verification

**Manual testing:**

- Test in real Telegram after deployment
- Verify error handling (backend down, invalid input)

---

## Environment Variables

| Variable | Description | Source |
|----------|-------------|--------|
| `BOT_TOKEN` | Telegram bot token | @BotFather |
| `LMS_API_URL` | Backend API URL | Local: `http://localhost:42002` |
| `LMS_API_KEY` | Backend API key | `.env.docker.secret` |
| `LLM_API_KEY` | Qwen Code API key | Qwen proxy setup |
| `LLM_API_BASE_URL` | LLM endpoint | `http://localhost:42005/v1` |
| `LLM_API_MODEL` | Model name | `coder-model` |

---

## File Structure

```
bot/
├── bot.py              # Entry point (--test + Telegram)
├── config.py           # Environment variable loading
├── pyproject.toml      # Dependencies
├── .env.bot.example    # Example environment file
├── PLAN.md             # This document
├── handlers/
│   ├── __init__.py
│   ├── start.py        # /start handler
│   ├── help.py         # /help handler
│   ├── health.py       # /health handler
│   ├── labs.py         # /labs handler
│   ├── scores.py       # /scores handler
│   └── intent_router.py # Task 3: LLM routing
└── services/
    ├── __init__.py
    ├── lms_client.py   # Task 2: LMS API client
    └── llm_client.py   # Task 3: LLM client
```
