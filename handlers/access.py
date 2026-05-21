import asyncio
import time

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import CHANNEL_ID
from database import (
    get_keyword, set_user_access, increment_keyword_uses,
    get_user_has_access, get_last_keyword_time, update_last_keyword_time,
    add_user,
)
from keyboards.user import subscribe_keyboard

router = Router()

COOLDOWN_SECONDS = 60
REMINDER_DELAY = 600  # 10 минут

# Хранит активные задачи напоминаний: user_id -> asyncio.Task
pending_reminders: dict[int, asyncio.Task] = {}


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status not in ["left", "kicked", "banned"]
    except TelegramBadRequest:
        return False


def cancel_reminder(user_id: int):
    task = pending_reminders.pop(user_id, None)
    if task and not task.done():
        task.cancel()


def start_reminder(bot: Bot, user_id: int, word: str, reward: str):
    cancel_reminder(user_id)
    task = asyncio.create_task(reminder_task(bot, user_id, word, reward))
    pending_reminders[user_id] = task


async def reminder_task(bot: Bot, user_id: int, word: str, reward: str):
    """Два напоминания с задержкой 10 минут — как в Instagram-боте."""

    await asyncio.sleep(REMINDER_DELAY)
    if await get_user_has_access(user_id):
        return
    if await is_subscribed(bot, user_id):
        await _grant_access(bot, user_id, word, reward)
        return
    try:
        await bot.send_message(
            user_id,
            "Чего же ты ждёшь? 😏\n\n"
            "Подпишись на канал и получи бонус — всё ещё ждёт тебя! 👇",
            reply_markup=subscribe_keyboard(CHANNEL_ID, word),
        )
    except Exception:
        pending_reminders.pop(user_id, None)
        return

    await asyncio.sleep(REMINDER_DELAY)
    if await get_user_has_access(user_id):
        return
    if await is_subscribed(bot, user_id):
        await _grant_access(bot, user_id, word, reward)
        return
    try:
        await bot.send_message(
            user_id,
            "⏰ Время вышло, бонуса не будет.\n\n"
            "Но ты всегда можешь подписаться на канал — там много полезного! 👇",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="📢 Перейти в канал",
                    url=f"https://t.me/{CHANNEL_ID.lstrip('@')}",
                )
            ]]),
        )
    except Exception:
        pass

    pending_reminders.pop(user_id, None)


async def _grant_access(bot: Bot, user_id: int, word: str, reward: str):
    cancel_reminder(user_id)
    await set_user_access(user_id)
    await increment_keyword_uses(word)
    try:
        await bot.send_message(
            user_id,
            f"✅ Отлично! Подписка подтверждена.\n\nВот твой бонус:\n\n{reward}",
        )
    except Exception:
        pass
    pending_reminders.pop(user_id, None)


@router.message(F.text & ~F.text.startswith("/"))
async def handle_keyword(message: Message, bot: Bot):
    keyword = await get_keyword(message.text.strip())

    if not keyword:
        await message.answer("Не знаю такого кодового слова. Попробуй ещё раз. 🤔")
        return

    _, word, reward, _ = keyword
    user_id = message.from_user.id

    # Гарантируем что пользователь есть в базе (даже без /start)
    await add_user(user_id, message.from_user.username, message.from_user.first_name)

    # Уже получил доступ
    if await get_user_has_access(user_id):
        await message.answer(
            f"🎉 Ты уже получил доступ!\n\nВот твой бонус:\n\n{reward}"
        )
        return

    # Rate limiting: cooldown 60 секунд между попытками
    last_time = await get_last_keyword_time(user_id)
    elapsed = time.time() - last_time
    if elapsed < COOLDOWN_SECONDS:
        wait = int(COOLDOWN_SECONDS - elapsed)
        await message.answer(
            f"⏳ Подожди ещё {wait} сек. перед следующей попыткой."
        )
        return

    # Сохраняем время запроса
    await update_last_keyword_time(user_id, time.time())

    if await is_subscribed(bot, user_id):
        await set_user_access(user_id)
        await increment_keyword_uses(word)
        await message.answer(
            f"✅ Отлично! Подписка подтверждена.\n\nВот твой бонус:\n\n{reward}"
        )
    else:
        await message.answer(
            "Чтобы получить доступ, нужно подписаться на канал.\n\n"
            "Подпишись и нажми кнопку ниже 👇",
            reply_markup=subscribe_keyboard(CHANNEL_ID, word),
        )
        start_reminder(bot, user_id, word, reward)


@router.callback_query(F.data.startswith("check_sub:"))
async def recheck_subscription(callback: CallbackQuery, bot: Bot):
    word = callback.data.split(":", 1)[1]
    keyword = await get_keyword(word)

    if not keyword:
        await callback.answer("Кодовое слово больше не действует.", show_alert=True)
        return

    _, kw_word, reward, _ = keyword
    user_id = callback.from_user.id

    if await get_user_has_access(user_id):
        await callback.answer("Ты уже получил доступ! 🎉", show_alert=True)
        return

    if await is_subscribed(bot, user_id):
        cancel_reminder(user_id)
        await set_user_access(user_id)
        await increment_keyword_uses(kw_word)
        await callback.message.edit_text(
            f"✅ Отлично! Подписка подтверждена.\n\nВот твой бонус:\n\n{reward}"
        )
    else:
        await callback.answer(
            "Ты ещё не подписан. Подпишись на канал и нажми кнопку снова.",
            show_alert=True,
        )
