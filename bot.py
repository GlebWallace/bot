import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PROXY_URL = os.getenv("HTTPS_PROXY")

logging.basicConfig(level=logging.INFO)

# --- Инициализация бота (с прокси, если задан) ---
if PROXY_URL:
    session = AiohttpSession(proxy=PROXY_URL)
    bot = Bot(token=BOT_TOKEN, session=session)
    logging.info(f"Бот запущен с прокси: {PROXY_URL}")
else:
    bot = Bot(token=BOT_TOKEN)
    logging.info("Бот запущен без прокси")

dp = Dispatcher()

# Путь к картинке рядом с bot.py
PHOTO_PATH = Path(__file__).parent / "photo.jpg"

# --- Текст приветствия ---
START_TEXT = (
    "<b>ГЛЕБ ЗАРОВНЯЕВ</b>\n\n"
    "Командой был разработан ряд сервисов для реализации ваших проектов, "
    "для презентации наших проектов и отображения концептуальной идеи бренда.\n\n"
    "Для получения интересующей вас информации используйте кнопки, "
    "либо выберите команды из предложенных."
)

# --- Клавиатура ---
def get_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Синяя кнопка — «Обо мне» (primary стиль в Bot API задаётся через color)
    builder.row(
        InlineKeyboardButton(
            text="Обо мне",
            callback_data="about",
            style="primary",  # синяя
        )
    )
    builder.row(
        InlineKeyboardButton(text="Профиль", callback_data="profile"),
        InlineKeyboardButton(text="Сайт", url="https://example.com"),
    )
    builder.row(
        InlineKeyboardButton(text="Документация", callback_data="docs"),
    )
    return builder.as_markup()

# --- /start ---
@dp.message(CommandStart())
async def cmd_start(message: Message):
    logging.info(f"/start от {message.from_user.id}")
    photo = FSInputFile(PHOTO_PATH)
    await message.answer_photo(
        photo=photo,
        caption=START_TEXT,
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
    )

# --- Обработчики кнопок ---
@dp.callback_query(F.data == "about")
async def cb_about(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "<b>Обо мне</b>\n\n"
        "Глеб Заровняев — основатель и руководитель команды разработки. "
        "Здесь можно разместить короткое описание, ссылки на соцсети и контакты."
    )

@dp.callback_query(F.data == "profile")
async def cb_profile(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "<b>Профиль</b>\n\n"
        "Здесь будет информация о вашем профиле, портфолио или резюме."
    )

@dp.callback_query(F.data == "docs")
async def cb_docs(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "<b>Документация</b>\n\n"
        "Здесь будет ссылка на документацию проекта, инструкции и т.д."
    )

async def main():
    logging.info("Запуск polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
