from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from google import genai
import httpx


async def list_available_openai_compatible_models(url: str, api_key: str) -> list[str]:
    # Special handling for Ollama Cloud
    if "ollama.com" in url:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{url.rstrip('/')}/tags",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30.0,
            )
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                return [m["name"] for m in models]
            return []

    client = AsyncOpenAI(api_key=api_key, base_url=url)
    models = (await client.models.list()).data
    if models:
        return list(map(lambda x: x.id, models))
    return []


async def list_available_anthropic_models(api_key: str) -> list[str]:
    client = AsyncAnthropic(api_key=api_key)
    return list(map(lambda x: x.id, (await client.models.list(limit=50)).data))


async def list_available_google_models(api_key: str) -> list[str]:
    client = genai.Client(api_key=api_key)
    return list(map(lambda x: x.name, client.models.list(config={"page_size": 50})))
