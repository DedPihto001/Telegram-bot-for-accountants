import asyncio
import logging
import socket

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from openai import APIConnectionError, APIError, RateLimitError

from api_client import APIClient
from config import load_settings
from context_manager import ContextManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

settings = load_settings()
api_client = APIClient(
    api_key=settings.api_key,
    model_name=settings.model_name,
    temperature=settings.temperature,
    max_tokens=settings.max_tokens,
    base_url=settings.api_base_url,
    provider=settings.api_provider,
)
context_manager = ContextManager()

dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer("Привет! Отправьте сообщение, и я сохраню контекст диалога. Для очистки: /reset")


@dp.message(Command("reset"))
@dp.message(F.text.lower() == "очистить контекст")
async def reset_context(message: Message) -> None:
    if message.from_user:
        context_manager.clear(message.from_user.id)
    await message.answer("Контекст диалога очищен.")


@dp.message()
async def chat(message: Message) -> None:
    if not message.text or not message.from_user:
        await message.answer("Пожалуйста, отправьте текстовое сообщение.")
        return

    user_id = message.from_user.id
    context_manager.add(user_id, "user", message.text)
    messages = context_manager.get(user_id, settings.system_prompt)

    try:
        reply, usage = await api_client.complete(messages)
        context_manager.add(user_id, "assistant", reply)

        usage_text = ""
        if usage:
            usage_text = f"\n\nТокены: input={usage['input']}, output={usage['output']}, total={usage['total']}"
        await message.answer(reply + usage_text)
    except RateLimitError:
        await message.answer("Сервис временно ограничил запросы. Повторите попытку позже.")
    except APIConnectionError:
        await message.answer("Не удалось подключиться к API модели. Проверьте интернет-соединение и адрес API.")
    except APIError:
        await message.answer("API модели вернуло ошибку. Проверьте модель, параметры и ключ доступа.")


@dp.errors()
async def global_error_handler(event) -> bool:
    logger.exception("Непредвиденная ошибка обработчика", exc_info=event.exception)
    return True


async def main() -> None:
    connector = aiohttp.TCPConnector(family=socket.AF_INET)
    async with aiohttp.ClientSession(connector=connector) as client_session:
        telegram_session = AiohttpSession(client_session=client_session)
        bot = Bot(settings.bot_token, session=telegram_session)

        while True:
            try:
                await dp.start_polling(bot)
            except TelegramNetworkError:
                logger.exception("Не удалось подключиться к Telegram; повтор через 10 секунд")
                await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
