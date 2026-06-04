import logging

import discord

from .handlers import handle_message
from .openrouter_client import fetch_free_models
from .router import route_message

logger = logging.getLogger(__name__)


class AIAgentClient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_ready(self) -> None:
        logger.info("Bot online as %s (ID: %s)", self.user, self.user.id)
        try:
            await fetch_free_models()
        except Exception as e:
            logger.error("Failed to pre-fetch free models: %s", e)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        is_dm = isinstance(message.channel, discord.DMChannel)
        is_guild_channel = isinstance(message.channel, (discord.TextChannel, discord.Thread))

        if not (is_dm or is_guild_channel):
            return

        logger.debug(
            "Message from %s in %s: %r",
            message.author,
            "DM" if is_dm else message.channel.name,
            message.content[:80],
        )

        agent = route_message(message.content)

        try:
            await handle_message(message, agent)
        except Exception as e:
            logger.exception("Error handling message: %s", e)
            try:
                await message.channel.send(
                    "An unexpected error occurred. Please try again."
                )
            except Exception:
                pass
