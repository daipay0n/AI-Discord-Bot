# Discord AI Agent

A production-ready Discord bot with 6 AI agents powered by OpenRouter's free models.

## Agents & Routing

Messages are routed by keyword (first match wins). The bot responds to **all server messages** and **DMs** — no @mention needed.

| Agent | Trigger Keywords |
|---|---|
| **Coding Expert** | code, python, javascript, debug, error, sql, api, github, html, css, ... |
| **Study Assistant** | math, homework, physics, chemistry, biology, exam, theorem, ... |
| **Research Assistant** | research, compare, vs, summary, history, statistics, analyze, ... |
| **Writing Assistant** | write, essay, email, article, proofread, resume, cover letter, ... |
| **Translation Assistant** | translate, bangla, bengali, বাংলা, or any Bengali Unicode text |
| **Main Brain** | Everything else (fallback) |

## Setup

1. Set secrets in Replit:
   - `DISCORD_BOT_TOKEN` — from [Discord Developer Portal](https://discord.com/developers/applications)
   - `OPENROUTER_API_KEY` — from [openrouter.ai/keys](https://openrouter.ai/keys)

2. Enable **Message Content Intent** in your bot's settings on the Discord Developer Portal.

3. The "Discord AI Agent" workflow starts automatically.

## How It Works

- On startup, fetches all current `:free` models from OpenRouter live (no hardcoded model IDs)
- Builds a fallback queue: preferred model first, then all others shuffled randomly
- Skips models that return 429, 502, 503, or 404
- Splits responses > 2000 chars at newlines (Discord's limit)
- Shows typing indicator while processing

## Railway Deployment

Two deployment configurations are included:

- `railway.toml` + `nixpacks.toml` at root — for Railway with default root directory
- `discord-bot/railway.toml` + `discord-bot/nixpacks.toml` — for Railway with root set to `discord-bot/`
