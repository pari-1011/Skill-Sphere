from free_api_client import ask_ai

def ask_azure_openai(messages):
    """Compatibility wrapper to route legacy Azure OpenAI calls to the free API client."""
    return ask_ai(messages, max_tokens=500, temperature=1.0)
