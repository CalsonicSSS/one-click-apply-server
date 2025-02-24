from app.config import get_settings
from anthropic import AsyncAnthropic
from typing import Optional, List

main_config_settings = get_settings()
claude_client = AsyncAnthropic(api_key=main_config_settings.CLAUDE_API_KEY)


async def claude_message_api(model: str, system_prompt: str, messages: List[dict], temp: int, max_tokens: int):

    response = await claude_client.messages.create(
        model=model,
        system=system_prompt,
        messages=messages,
        temperature=temp,
        # specifies the maximum number of tokens that the model will generate in its response. It does not include the tokens from the input message
        max_tokens=max_tokens,
    )

    return response
