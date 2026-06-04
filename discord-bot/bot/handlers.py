import logging
from typing import Optional

import discord

from .models import Agent, AGENTS
from .openrouter_client import chat_completion, _free_models, fetch_free_models

logger = logging.getLogger(__name__)

MAX_DISCORD_LENGTH = 2000
HELP_COMMANDS = {"!help", "!agents", "!commands"}
STATUS_COMMANDS = {"!status", "!models", "!info"}


def _build_help_message() -> str:
    lines = [
        "**🤖 Discord AI Agent — Help**\n",
        "I route your message to the best AI agent automatically based on keywords.\n",
    ]
    for agent in AGENTS:
        if agent.name == "Main Brain":
            lines.append(f"**🧠 {agent.name}**")
            lines.append("↳ Handles everything else — general questions, chat, anything\n")
        else:
            icons = {
                "Coding Expert": "💻",
                "Study Assistant": "📚",
                "Research Assistant": "🔍",
                "Writing Assistant": "✍️",
            }
            icon = icons.get(agent.name, "🤖")
            kws = ", ".join(f"`{k}`" for k in agent.keywords[:8])
            if len(agent.keywords) > 8:
                kws += f" +{len(agent.keywords) - 8} more"
            lines.append(f"**{icon} {agent.name}**")
            lines.append(f"↳ Keywords: {kws}\n")

    lines.append("**⚙️ Commands**")
    lines.append("`!help` — show this message")
    lines.append("`!status` — show available AI models and agent assignments")
    return "\n".join(lines)


def _build_status_message() -> str:
    total = len(_free_models)
    lines = [
        "**📊 Discord AI Agent — Status**\n",
        f"**Free models loaded:** {total}\n",
    ]
    icons = {
        "Coding Expert": "💻",
        "Study Assistant": "📚",
        "Research Assistant": "🔍",
        "Writing Assistant": "✍️",
        "Main Brain": "🧠",
    }
    lines.append("**Agent → Primary Model**")
    for agent in AGENTS:
        icon = icons.get(agent.name, "🤖")
        primary = agent.preferred_models[0] if agent.preferred_models else "any free model"
        fallbacks = len(agent.preferred_models) - 1
        lines.append(f"{icon} **{agent.name}** → `{primary}` (+{fallbacks} fallbacks)")
    lines.append(f"\n**Total fallback pool:** {total} free models from OpenRouter")
    return "\n".join(lines)


def _split_response(text: str, max_len: int = MAX_DISCORD_LENGTH) -> list[str]:
    if len(text) <= max_len:
        return [text]
    chunks: list[str] = []
    current = ""
    for line in text.splitlines(keepends=True):
        if len(current) + len(line) > max_len:
            if current:
                chunks.append(current)
                current = ""
            if len(line) > max_len:
                while len(line) > max_len:
                    chunks.append(line[:max_len])
                    line = line[max_len:]
                current = line
            else:
                current = line
        else:
            current += line
    if current:
        chunks.append(current)
    return chunks


async def handle_message(message: discord.Message, agent: Agent) -> None:
    content = message.content.strip()
    lower = content.lower()

    if lower in HELP_COMMANDS:
        await message.channel.send(_build_help_message())
        return

    if lower in STATUS_COMMANDS:
        if not _free_models:
            async with message.channel.typing():
                await fetch_free_models()
        await message.channel.send(_build_status_message())
        return

    messages = [
        {"role": "system", "content": agent.system_prompt},
        {"role": "user", "content": content},
    ]

    async with message.channel.typing():
        response: Optional[str] = await chat_completion(
            messages=messages,
            preferred_models=agent.preferred_models,
        )

    if response is None:
        await message.channel.send(
            f"**[{agent.name}]**\nSorry, all AI models are currently unavailable. Please try again later."
        )
        return

    header = f"**[{agent.name}]**\n"
    full_response = header + response
    for chunk in _split_response(full_response):
        await message.channel.send(chunk)
