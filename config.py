import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    api_key: str
    model_name: str
    temperature: float
    max_tokens: int
    system_prompt: str
    api_base_url: str | None


def required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Не задана обязательная переменная окружения {name}")
    return value


def load_settings() -> Settings:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    api_base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None

    if not api_key:
        api_key = os.getenv("GENAPI_KEY", "").strip()
        api_base_url = os.getenv("GENAPI_BASE_URL", "").strip() or api_base_url

    if not api_key:
        raise RuntimeError("Не задан OPENAI_API_KEY или GENAPI_KEY")

    try:
        temperature = float(os.getenv("TEMPERATURE", "0.2"))
        max_tokens = int(os.getenv("MAX_TOKENS", "100"))
    except ValueError as exc:
        raise RuntimeError("TEMPERATURE должен быть числом, а MAX_TOKENS — целым числом") from exc

    if not 0 <= temperature <= 2:
        raise RuntimeError("TEMPERATURE должен находиться в диапазоне от 0 до 2")
    if max_tokens < 1:
        raise RuntimeError("MAX_TOKENS должен быть больше нуля")

    return Settings(
        bot_token=required("BOT_TOKEN"),
        api_key=api_key,
        model_name=required("MODEL_NAME"),
        temperature=temperature,
        max_tokens=max_tokens,
        system_prompt=os.getenv("SYSTEM_PROMPT", "Ты полезный ассистент.").strip(),
        api_base_url=api_base_url,
    )
