# Lab 7 — Build a Client with an AI Coding Agent

[Sync your fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork#syncing-a-fork-branch-from-the-command-line) regularly — the lab gets updated.

## Product brief

> Build a Telegram bot that lets users interact with the LMS backend through chat. Users should be able to check system health, browse labs and scores, and ask questions in plain language. The bot should use an LLM to understand what the user wants and fetch the right data. Deploy it alongside the existing backend on the VM.

This is what a customer might tell you. Your job is to turn it into a working product using an AI coding agent (Qwen Code) as your development partner.

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  Telegram    │────▶│  Your Bot                        │   │
│  │  User        │◀────│  (aiogram / python-telegram-bot) │   │
│  └──────────────┘     └──────┬───────────────────────────┘   │
│                              │                               │
│                              │ slash commands + plain text    │
│                              ├───────▶ /start, /help         │
│                              ├───────▶ /health, /labs        │
│                              ├───────▶ intent router ──▶ LLM │
│                              │                    │          │
│                              │                    ▼          │
│  ┌──────────────┐     ┌──────┴───────┐    tools/actions      │
│  │  Docker      │     │  LMS Backend │◀───── GET /items      │
│  │  Compose     │     │  (FastAPI)   │◀───── GET /analytics  │
│  │              │     │  + PostgreSQL│◀───── POST /sync      │
│  └──────────────┘     └──────────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

## Requirements

### P0 — Must have

1. Testable handler architecture — handlers work without Telegram
2. CLI test mode: `cd bot && uv run bot.py --test "/command"` prints response to stdout
3. `/start` — welcome message
4. `/help` — lists all available commands
5. `/health` — calls backend, reports up/down status
6. `/labs` — lists available labs
7. `/scores <lab>` — per-task pass rates
8. Error handling — backend down produces a friendly message, not a crash

### P1 — Should have

1. Natural language intent routing — plain text interpreted by LLM
2. All 9 backend endpoints wrapped as LLM tools
3. Inline keyboard buttons for common actions
4. Multi-step reasoning (LLM chains multiple API calls)

### P2 — Nice to have

1. Rich formatting (tables, charts as images)
2. Response caching
3. Conversation context (multi-turn)

### P3 — Deployment

1. Bot containerized with Dockerfile
2. Added as service in `docker-compose.yml`
3. Deployed and running on VM
4. README documents deployment

## Learning advice

Notice the progression above: **product brief** (vague customer ask) → **prioritized requirements** (structured) → **task specifications** (precise deliverables + acceptance criteria). This is how engineering work flows.

You are not following step-by-step instructions — you are building a product with an AI coding agent. The learning comes from planning, building, testing, and debugging iteratively.

## Learning outcomes

By the end of this lab, you should be able to say:

1. I turned a vague product brief into a working Telegram bot.
2. I can ask it questions in plain language and it fetches the right data.
3. I used an AI coding agent to plan and build the whole thing.

## Tasks

### Prerequisites

1. Complete the [lab setup](./lab/setup/setup-simple.md#lab-setup)

> **Note**: First time in this course? Do the [full setup](./lab/setup/setup-full.md#lab-setup) instead.

### Required

1. [Plan and Scaffold](./lab/tasks/required/task-1.md) — P0: project structure + `--test` mode
2. [Backend Integration](./lab/tasks/required/task-2.md) — P0: slash commands + real data
3. [Intent-Based Natural Language Routing](./lab/tasks/required/task-3.md) — P1: LLM tool use
4. [Containerize and Document](./lab/tasks/required/task-4.md) — P3: containerize + deploy

## Deploy

### Prerequisites

Before deploying the bot, ensure you have:

1. **Telegram bot token** from @BotFather
2. **LLM API key** from Qwen Code API (running on your VM at `http://localhost:42005/v1`)
3. **LMS API key** matching your backend configuration

### Configure environment variables

On your VM, edit `.env.docker.secret`:

```bash
cd ~/se-toolkit-lab-7
nano .env.docker.secret
```

Add these lines (replace with your actual values):

```text
BOT_TOKEN=your-telegram-bot-token-here
LLM_API_KEY=your-qwen-api-key
LLM_API_MODEL=coder-model
```

Ensure `LMS_API_KEY` matches the value in your backend configuration.

### Deploy with Docker Compose

1. **Stop the background bot process** (if running from Task 3):

   ```bash
   pkill -f "bot.py" 2>/dev/null || true
   ```

2. **Start all services** (backend + bot):

   ```bash
   cd ~/se-toolkit-lab-7
   docker compose --env-file .env.docker.secret up --build -d
   ```

3. **Verify services are running**:

   ```bash
   docker compose --env-file .env.docker.secret ps
   ```

   You should see `bot`, `backend`, `postgres`, `pgadmin`, and `caddy` all running.

4. **Check bot logs**:

   ```bash
   docker compose --env-file .env.docker.secret logs bot --tail 30
   ```

   Look for "Bot is running" and no Python tracebacks.

### Verify in Telegram

1. Open your bot in Telegram
2. Send `/start` — should receive a welcome message
3. Send `/health` — should see backend status
4. Type "what labs are available?" — should list labs from the backend
5. Type "which lab has the lowest pass rate?" — should analyze and respond with data

### Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot container restarts | Check logs: `docker compose logs bot` |
| LLM queries fail | Ensure `LLM_API_BASE_URL` uses `host.docker.internal:42005/v1` |
| Backend connection fails | `LMS_API_URL` must be `http://backend:8000` (not localhost) |
| Missing env var error | Add the variable to `.env.docker.secret` and restart |
