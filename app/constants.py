LLM_MODELS = {"claude": {"haiku": "claude-haiku-4-5-20251001", "sonnet": "claude-sonnet-4-6"}}
# All generation now runs on Sonnet 4.6 (Claude-only — no OpenAI fallback).
TARGET_LLM_MODEL_SONNET = LLM_MODELS["claude"]["sonnet"]

# Credit packages configuration
CREDITS_PACKAGES = {"15": {"price": 4.99, "credits": 15}, "40": {"price": 9.99, "credits": 40}}
