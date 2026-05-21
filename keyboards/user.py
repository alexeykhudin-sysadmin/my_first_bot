from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def subscribe_keyboard(channel_username: str, keyword: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📢 Подписаться на канал",
            url=f"https://t.me/{channel_username.lstrip('@')}"
        )],
        [InlineKeyboardButton(
            text="✅ Я подписался",
            callback_data=f"check_sub:{keyword}"
        )],
    ])
