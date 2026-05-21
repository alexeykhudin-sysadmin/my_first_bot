from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats")],
        [InlineKeyboardButton(text="🔑 Кодовые слова", callback_data="admin:keywords")],
        [InlineKeyboardButton(text="➕ Добавить слово", callback_data="admin:add_keyword")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin:broadcast")],
    ])


def keywords_keyboard(keywords: list) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text=f"🗑 {word} (использований: {uses})",
            callback_data=f"admin:del:{word}"
        )]
        for word, _, uses in keywords
    ]
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin:menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
