import logging

from openai import APIConnectionError, APIError, AsyncOpenAI, RateLimitError

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(
        self,
        api_key: str,
        model_name: str,
        temperature: float,
        max_tokens: int,
        base_url: str | None = None,
    ) -> None:
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def complete(self, messages: list[dict[str, str]]) -> tuple[str, dict[str, int] | None]:
        logger.info(
            "LLM request: model=%s temperature=%s max_tokens=%s messages=%s",
            self.model_name,
            self.temperature,
            self.max_tokens,
            len(messages),
        )

        try:
            try:
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
            except APIError as exc:
                error_text = str(exc).lower()
                if "temperature" not in error_text and "max_tokens" not in error_text:
                    raise
                logger.warning("Использую параметры совместимости для выбранной модели")
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    max_completion_tokens=self.max_tokens,
                )

            usage = None
            if response.usage:
                usage = {
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens,
                    "total": response.usage.total_tokens,
                }

            content = response.choices[0].message.content or ""
            return content, usage
        except RateLimitError as exc:
            logger.error("LLM rate limit exceeded: %s", type(exc).__name__)
            raise
        except APIConnectionError as exc:
            logger.error("LLM connection error: %s", type(exc).__name__)
            raise
        except APIError as exc:
            logger.error("LLM API error: %s", type(exc).__name__)
            raise
