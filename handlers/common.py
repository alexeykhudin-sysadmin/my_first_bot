from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

router = Router()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ℹ️ О боте"), KeyboardButton(text="🆘 Помощь")],
    ],
    resize_keyboard=True,
)


def about_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="GitHub", url="https://github.com/alexeykhudin-sysadmin/my_first_bot"),
            InlineKeyboardButton(text="Автор", callback_data="author"),
        ],
    ])


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Используй кнопки внизу или /help.",
        reply_markup=main_keyboard,
    )


@router.message(Command("help"))
@router.message(F.text == "🆘 Помощь")
async def cmd_help(message: Message):
    await message.answer(
        "Доступные команды:\n"
        "/start — начало работы\n"
        "/help — список команд\n\n"
        "Или используй кнопки внизу экрана.",
        reply_markup=main_keyboard,
    )


@router.message(F.text == "ℹ️ О боте")
async def about(message: Message):
    await message.answer(
        "Это мой первый Telegram-бот на aiogram 3! 🤖\n"
        "Исходный код открыт на GitHub.",
        reply_markup=about_inline(),
    )


@router.callback_query(F.data == "author")
async def callback_author(callback: CallbackQuery):
    await callback.answer("Разработчик: alexeykhudin-sysadmin 👨‍💻", show_alert=True)
