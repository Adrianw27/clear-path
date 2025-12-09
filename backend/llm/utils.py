import re

def clean_llm_response(response_text: str) -> str:
    """
    Removes Markdown code blocks (```json ... ```) from LLM responses.
    """

    cleaned = re.sub(r"^```[a-zA-Z]*\n", "", response_text.strip())
    cleaned = re.sub(r"\n```$", "", cleaned)
    return cleaned.strip()
