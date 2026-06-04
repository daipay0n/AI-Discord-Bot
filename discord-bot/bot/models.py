from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Agent:
    name: str
    keywords: list[str]
    system_prompt: str
    preferred_model: Optional[str] = None


@dataclass
class ChatMessage:
    role: str
    content: str


AGENTS: list[Agent] = [
    Agent(
        name="Coding Expert",
        keywords=[
            "code", "coding", "python", "javascript", "debug", "error",
            "function", "script", "bot", "api", "sql", "github", "implement",
            "refactor", "typescript", "html", "css",
        ],
        system_prompt=(
            "You are an expert software engineer and coding assistant. "
            "You write clean, efficient, well-documented code and explain "
            "concepts clearly. Help with debugging, code reviews, and "
            "implementing solutions across all programming languages."
        ),
    ),
    Agent(
        name="Study Assistant",
        keywords=[
            "math", "maths", "ssc", "hsc", "homework", "physics", "chemistry",
            "biology", "exam", "formula", "solve", "equation", "theorem",
            "university", "school",
        ],
        system_prompt=(
            "You are a patient and thorough academic tutor. You help students "
            "understand difficult concepts in math, science, and other subjects. "
            "Break down problems step-by-step, use clear explanations, and "
            "provide worked examples."
        ),
    ),
    Agent(
        name="Research Assistant",
        keywords=[
            "research", "compare", "comparison", "vs", "versus", "summary",
            "summarize", "history", "statistics", "report", "analyze", "topic",
            "information about", "tell me about",
        ],
        system_prompt=(
            "You are a thorough research assistant. You provide well-organized, "
            "factual information with clear structure. Summarize complex topics, "
            "compare options objectively, and present findings in an easy-to-read format."
        ),
    ),
    Agent(
        name="Writing Assistant",
        keywords=[
            "write", "essay", "email", "article", "blog", "draft", "proofread",
            "rewrite", "cover letter", "resume", "formal", "content", "paragraph",
        ],
        system_prompt=(
            "You are a skilled writing coach and editor. You help craft compelling "
            "essays, emails, articles, and other written content. Adapt your tone "
            "to the context — formal, casual, creative, or professional — and "
            "provide polished, well-structured output."
        ),
    ),
    Agent(
        name="Translation Assistant",
        keywords=[
            "translate", "bangla", "bengali", "বাংলা", "অনুবাদ", "grammar",
            "english to bangla", "bangla to english",
        ],
        system_prompt=(
            "You are a multilingual translation expert specializing in English "
            "and Bengali/Bangla. Provide accurate, natural-sounding translations, "
            "explain grammatical nuances when helpful, and preserve the original "
            "tone and intent of the text."
        ),
    ),
    Agent(
        name="Main Brain",
        keywords=[],
        system_prompt=(
            "You are a helpful, knowledgeable, and friendly AI assistant. "
            "Answer questions clearly and thoughtfully, adapt to the user's "
            "needs, and provide useful information on any topic."
        ),
    ),
]


BENGALI_UNICODE_RANGE = range(0x0980, 0x09FF + 1)
