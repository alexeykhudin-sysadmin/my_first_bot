from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import add_user

router = Router()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ℹ️ О боте"), KeyboardButton(text="🆘 Помощь")],
    ],
    resize_keyboard=True,
)


@router.message(Command("start"))
async def cmd_start(message: Message):
    await add_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Напиши кодовое слово, чтобы получить доступ.\n"
        "Используй /help чтобы узнать больше.",
        reply_markup=main_keyboard,
    )


@router.message(Command("help"))
@router.message(F.text == "🆘 Помощь")
async def cmd_help(message: Message):
    await message.answer(
        "Как получить доступ:\n\n"
        "1. Подпишись на наш канал\n"
        "2. Напиши кодовое слово боту\n"
        "3. Нажми кнопку «Я подписался»\n"
        "4. Получи бонус! 🎁\n\n"
        "Команды:\n"
        "/start — начало\n"
        "/help — эта справка",
        reply_markup=main_keyboard,
    )


@router.message(F.text == "ℹ️ О боте")
async def about(message: Message):
    await message.answer(
        "Этот бот выдаёт доступ к материалам\n"
        "после проверки подписки на канал. 🤖",
        reply_markup=main_keyboard,
    )
