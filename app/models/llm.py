from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import get_settings

main_config_settings = get_settings()

# Initialize the model
def initialize_llm( model_name: str, temperature: float, max_tokens: int):
    return ChatOpenAI(model=model_name, temperature=temperature, max_tokens=max_tokens, api_key=main_config_settings.OPENAI_API_KEY)
