import json
import re
from typing import Any, Dict
from app.custom_exceptions import LLMResponseParsingError


def parse_llm_json_response(response_text: str) -> Dict[str, Any]:
    # Step 1: Try direct JSON parsing first (fastest approach)
    try:
        return json.loads(response_text, strict=False)
    except json.JSONDecodeError:
        pass

    # Step 2: Extract JSON block if the response includes markdown code blocks or other text
    json_pattern = r"```(?:json)?\s*([\s\S]*?)```|(\{[\s\S]*\})"
    json_match = re.search(json_pattern, response_text)

    if json_match:
        # Get the first group that matched (either inside code block or standalone {})
        json_str = next(filter(None, json_match.groups()))
        try:
            return json.loads(json_str, strict=False)
        except json.JSONDecodeError:
            pass

    # Step 3: More aggressive extraction - find the outermost JSON object
    json_content_match = re.search(r"({[\s\S]*})", response_text)
    if json_content_match:
        json_str = json_content_match.group(1)

        # Clean up common JSON issues
        json_str = json_str.replace("\n", " ").replace("\r", "")

        # Fix trailing commas
        json_str = re.sub(r",\s*}", "}", json_str)
        json_str = re.sub(r",\s*]", "]", json_str)

        try:
            return json.loads(json_str, strict=False)
        except json.JSONDecodeError:
            pass

    # If all parsing attempts fail
    raise LLMResponseParsingError(error_detail_message="Something went wrong when try to prepare response for you")
