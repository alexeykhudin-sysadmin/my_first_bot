from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery

from config import CHANNEL_ID
from database import get_keyword, set_user_access, increment_keyword_uses
from keyboards.user import subscribe_keyboard

router = Router()


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status not in ["left", "kicked", "banned"]
    except TelegramBadRequest:
        return False


@router.message(F.text & ~F.text.startswith("/"))
async def handle_keyword(message: Message, bot: Bot):
    keyword = await get_keyword(message.text.strip())

    if not keyword:
        await message.answer("Не знаю такого кодового слова. Попробуй ещё раз. 🤔")
        return

    _, word, reward, _ = keyword

    if await is_subscribed(bot, message.from_user.id):
        await set_user_access(message.from_user.id)
        await increment_keyword_uses(word)
        await message.answer(f"✅ Отлично! Подписка подтверждена.\n\nВот твой бонус:\n\n{reward}")
    else:
        await message.answer(
            "Чтобы получить доступ, нужно подписаться на канал.\n\n"
            "Подпишись и нажми кнопку ниже 👇",
            reply_markup=subscribe_keyboard(CHANNEL_ID, word),
        )


@router.callback_query(F.data.startswith("check_sub:"))
async def recheck_subscription(callback: CallbackQuery, bot: Bot):
    word = callback.data.split(":", 1)[1]
    keyword = await get_keyword(word)

    if not keyword:
        await callback.answer("Кодовое слово больше не действует.", show_alert=True)
        return

    _, kw_word, reward, _ = keyword

    if await is_subscribed(bot, callback.from_user.id):
        await set_user_access(callback.from_user.id)
        await increment_keyword_uses(kw_word)
        await callback.message.edit_text(
            f"✅ Отлично! Подписка подтверждена.\n\nВот твой бонус:\n\n{reward}"
        )
    else:
        await callback.answer(
            "Ты ещё не подписан. Подпишись на канал и нажми кнопку снова.",
            show_alert=True,
        )
