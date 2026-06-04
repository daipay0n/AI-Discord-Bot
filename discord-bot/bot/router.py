import logging

from .models import Agent, AGENTS, BENGALI_UNICODE_RANGE

logger = logging.getLogger(__name__)


def _has_bengali(text: str) -> bool:
    return any(ord(c) in BENGALI_UNICODE_RANGE for c in text)


def route_message(content: str) -> Agent:
    lower = content.lower()

    translation_agent = next(a for a in AGENTS if a.name == "Translation Assistant")
    main_brain = next(a for a in AGENTS if a.name == "Main Brain")

    if _has_bengali(content):
        logger.debug("Routing to Translation Assistant (Bengali detected)")
        return translation_agent

    for agent in AGENTS:
        if not agent.keywords:
            continue
        for kw in agent.keywords:
            if kw in lower:
                logger.debug("Routing to %s (keyword: %r)", agent.name, kw)
                return agent

    logger.debug("Routing to Main Brain (fallback)")
    return main_brain
