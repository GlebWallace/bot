import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ChatJoinRequest
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramForbiddenError

# Загружаем переменные окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
PROXY_URL = os.getenv("HTTPS_PROXY")  # Прокси для BotHost

logging.basicConfig(level=logging.INFO)

# Инициализация бота с поддержкой прокси
if PROXY_URL:
    session = AiohttpSession(proxy=PROXY_URL)
    bot = Bot(token=BOT_TOKEN, session=session)
    logging.info(f"Бот инициализирован с прокси: {PROXY_URL}")
else:
    bot = Bot(token=BOT_TOKEN)
    logging.info("Бот инициализирован без прокси")

dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    logging.info(f"Пользователь {user_id} запустил бота.")
    
    await message.answer(
        f"Привет! 👋\n\n"
        f"Я бот для обработки заявок в закрытый канал.\n"
        f"Теперь я смогу отправить тебе результат рассмотрения заявки.\n\n"
        f"Пожалуйста, подай заявку в канал. Ожидай ответа."
    )

@dp.chat_join_request()
async def handle_join_request(join_request: ChatJoinRequest):
    user_id = join_request.from_user.id
    user_name = join_request.from_user.full_name
    channel_id = join_request.chat.id

    logging.info(f"Новая заявка от {user_name} (ID: {user_id})")

    try:
        await bot.approve_chat_join_request(chat_id=channel_id, user_id=user_id)
        logging.info(f"Заявка от {user_id} одобрена.")
    except Exception as e:
        logging.error(f"Не удалось одобрить заявку: {e}")
        return

    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"✅ <b>Ваша заявка одобрена!</b>\n\nДобро пожаловать в канал, {user_name}."
        )
        logging.info(f"Сообщение отправлено пользователю {user_id}.")
    except TelegramForbiddenError:
        logging.warning(f"Пользователь {user_id} не запускал бота — сообщение не отправлено.")
    except Exception as e:
        logging.error(f"Ошибка отправки сообщения: {e}")

async def main():
    logging.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
