# Telegram mini-bot с контекстом диалога

Python 3.10+ | aiogram 3 | OpenAI/GenAPI SDK

## Настройка

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Заполните `.env`:

```dotenv
BOT_TOKEN=<токен Telegram BotFather>
API_PROVIDER=openai
OPENAI_API_KEY=<ключ OpenAI>
MODEL_NAME=gpt-5-mini-2025-08-07
TEMPERATURE=0.2
MAX_TOKENS=100
SYSTEM_PROMPT=Ты полезный ассистент.
```

Для OpenAI оставьте `API_PROVIDER=openai` и заполните `OPENAI_API_KEY`.

Для прокси GenAPI используйте OpenAI-совместимый режим:

```dotenv
BOT_TOKEN=<токен Telegram BotFather>
API_PROVIDER=genapi
GENAPI_KEY=<ключ GenAPI>
GENAPI_BASE_URL=https://proxy.gen-api.ru/v1
MODEL_NAME=<название модели в личном кабинете GenAPI>
TEMPERATURE=0.2
MAX_TOKENS=100
SYSTEM_PROMPT=Ты полезный ассистент.
```

Не публикуйте `.env` и не помещайте ключи в Git. Для OpenAI-формата используется `https://proxy.gen-api.ru/v1`, адрес можно переопределить через `GENAPI_BASE_URL`.

Запуск:

```powershell
py bot.py
```

Команды: `/start`, `/reset` и текст «очистить контекст».

## Выбранная конфигурация первого прогона

Основной прогон через GenAPI: модель `gpt-4.1`, `temperature=0.2`, `max_tokens=100`. Цель — сжатый и предсказуемый ответ. Рабочий endpoint — `https://proxy.gen-api.ru/v1`. Первый Telegram-прогон подтверждён ответом API HTTP 200 и использованием 126 токенов в диалоге.

## Таблица прогонов

| Модель | temperature | max_tokens | № прогона | Эффект (сжатость/креатив) | Токены (input/output/total) | Ориентировочная стоимость |
|---|---:|---:|---:|---|---|---:|
| gpt-4.1 через GenAPI | 0.2 | 100 | 1 | Сжатый и предсказуемый | 32 / 82 / 114 | По тарифу кабинета GenAPI |
| gpt-4.1 через GenAPI | 0.7 | 300 | 2 | Более развёрнутый и разнообразный | 32 / 95 / 127 | По тарифу кабинета GenAPI |
| gpt-4.1 через GenAPI | 1.0 | 500 | 3 | Не выполнен: HTTP 402, недостаточный баланс | Не получено | Не рассчитано |

## Расчёт стоимости OpenAI

Для прямого OpenAI:

- input: $0.25 за 1M токенов;
- output: $2.00 за 1M токенов;
- стоимость одного ответа = `input_tokens * 0.25 / 1_000_000 + output_tokens * 2.00 / 1_000_000`.

При использовании GenAPI применяются тарифы аккаунта GenAPI. Точный итоговый баланс и цену запросов нужно взять из личного кабинета: для прямого тарифа GenAPI ориентир из ответа API составлял около 0.5 ₽ за 1K input-токенов и 2 ₽ за 1K output-токенов, но для отчёта требуется фактическая история тарифов аккаунта.

## Подтверждение использования

- OpenAI напрямую: приложите скриншот Usage Dashboard с фильтром по проекту и периодом тестирования.
- GenAPI или другой прокси: приложите ID запросов из личного кабинета или скриншот истории вызовов.
- Фактические выводы API и usage внесены в таблицу после запуска.

## Скриншоты работы

- [Сброс контекста](/project/screenshots/01-reset.png)
- [Ответ и показ usage](/project/screenshots/02-context.png)
- [Состояние Telegram-чата при втором прогоне](/project/screenshots/03-run2-temperature-07.png)

Скриншоты демонстрируют успешный запуск бота, обработку `/reset` и вывод usage. Секреты Telegram и GenAPI на снимках не отображаются.

## Формат сдачи

Перед архивацией удалите `.env`, приложите только `.env.example`; ZIP не должен содержать ключи и токены.
