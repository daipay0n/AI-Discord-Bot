import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("discord.http").setLevel(logging.WARNING)
    logging.getLogger("discord.gateway").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def _validate_secrets() -> None:
    missing = []
    for key in ("DISCORD_BOT_TOKEN", "OPENROUTER_API_KEY"):
        val = os.environ.get(key, "").strip()
        if not val:
            missing.append(key)
    if missing:
        print(
            f"ERROR: Missing required environment variables: {', '.join(missing)}\n"
            "Set them in Replit Secrets or a .env file.",
            file=sys.stderr,
        )
        sys.exit(1)


def main() -> None:
    _configure_logging()
    _validate_secrets()

    logger = logging.getLogger(__name__)
    logger.info("Starting Discord AI Agent...")

    from bot.client import AIAgentClient

    token = os.environ["DISCORD_BOT_TOKEN"].strip()
    client = AIAgentClient()
    client.run(token, log_handler=None)


if __name__ == "__main__":
    main()
