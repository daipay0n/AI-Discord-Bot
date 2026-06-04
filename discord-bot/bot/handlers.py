import logging
from typing import Optional

import discord

from .memory import memory
from .models import Agent, AGENTS
from .openrouter_client import chat_completion

logger = logging.getLogger(__name__)

MAX_DISCORD_LENGTH = 2000
CLEAR_COMMANDS = {"!clear", "!reset", "!forget"}
HELP_COMMANDS = {"!help", "!agents", "!commands"}


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
    lines.append("`!clear` / `!reset` / `!forget` — wipe conversation memory and start fresh")
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
    channel_id = message.channel.id
    content = message.content.strip()

    if content.lower() in HELP_COMMANDS:
        await message.channel.send(_build_help_message())
        return

    if content.lower() in CLEAR_COMMANDS:
        memory.clear(channel_id)
        await message.channel.send(
            f"**[{agent.name}]**\nConversation memory cleared. Starting fresh!"
        )
        return

    memory.add(channel_id, "user", content)
    history = memory.get(channel_id)

    messages = [{"role": "system", "content": agent.system_prompt}] + history

    async with message.channel.typing():
        response: Optional[str] = await chat_completion(
            messages=messages,
            preferred_models=agent.preferred_models,
        )

    if response is None:
        memory.clear(channel_id)
        await message.channel.send(
            f"**[{agent.name}]**\nSorry, all AI models are currently unavailable. Please try again later."
        )
        return

    memory.add(channel_id, "assistant", response)

    header = f"**[{agent.name}]**\n"
    full_response = header + response
    chunks = _split_response(full_response)

    for chunk in chunks:
        await message.channel.send(chunk)
        logger.debug("Sent chunk of length %d", len(chunk))
