import logging

from .models import Agent, AGENTS

logger = logging.getLogger(__name__)


def route_message(content: str) -> Agent:
    lower = content.lower()
    main_brain = next(a for a in AGENTS if a.name == "Main Brain")

    for agent in AGENTS:
        if not agent.keywords:
            continue
        for kw in agent.keywords:
            if kw in lower:
                logger.debug("Routing to %s (keyword: %r)", agent.name, kw)
                return agent

    logger.debug("Routing to Main Brain (fallback)")
    return main_brain
