"""LLM Configuration settings."""


class LLMConfig:
    """Configuration settings for the LLM."""
    model: str = "gemini-2.5-flash-lite"
    max_tokens: int = 1024
    default_temp: float = 0.5
