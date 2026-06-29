from openai import OpenAI

from researchgraph.config import Settings, get_settings


def create_openrouter_client(settings: Settings | None = None) -> OpenAI:
    active_settings = settings or get_settings()
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=active_settings.openrouter_api_key,
        default_headers={
            'HTTP-Referer': active_settings.app_url,
            'X-OpenRouter-Title': active_settings.app_name
        }
    )