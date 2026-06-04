import logging
from typing import Optional

import discord

from .models import Agent
from .openrouter_client import chat_completion

logger = logging.getLogger(__name__)

MAX_DISCORD_LENGTH = 2000


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
    messages = [
        {"role": "system", "content": agent.system_prompt},
        {"role": "user", "content": message.content},
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
    chunks = _split_response(full_response)

    for chunk in chunks:
        await message.channel.send(chunk)
        logger.debug("Sent chunk of length %d", len(chunk))
