AVAILABLE_PROVIDERS = {
    "anthropic": {
        "models": [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
        ],
        "default": "claude-3-5-sonnet-20241022"
    },
    "openai": {
        "models": [
            "gpt-4o",
            "gpt-4o-2024-11-20",
            "gpt-4o-2024-08-06",
            "gpt-4o-2024-05-13",
            "gpt-4o-mini",
            "o1-preview",
            "o1-mini"
        ],
        "default": "gpt-4o-2024-11-20"
    }
}

MODEL_ALIASES = {
    # Anthropic shortcuts
    "sonnet": "anthropic:claude-3-5-sonnet-20241022",
    "haiku": "anthropic:claude-3-5-haiku-20241022",
    "opus": "anthropic:claude-3-opus-20240229",

    # OpenAI shortcuts
    "gpt4": "openai:gpt-4o-2024-11-20",
    "gpt4-mini": "openai:gpt-4o-mini",
    "o1": "openai:o1-preview",
}