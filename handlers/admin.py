from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from config import ADMIN_ID
from database import (
    add_keyword, delete_keyword, get_all_keywords,
    get_all_user_ids, get_stats,
)
from keyboards.admin import admin_menu, keywords_keyboard

router = Router()


class AddKeyword(StatesGroup):
    waiting_word = State()
    waiting_reward = State()


class Broadcast(StatesGroup):
    waiting_message = State()


def is_admin(user_id: int) -> bool:
    return user_id == int(ADMIN_ID)


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Панель администратора 🛠", reply_markup=admin_menu())


@router.callback_query(F.data == "admin:menu")
async def admin_back(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("Панель администратора 🛠", reply_markup=admin_menu())


@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    total, with_access = await get_stats()
    await callback.message.edit_text(
        f"📊 Статистика:\n\n"
        f"👥 Всего пользователей: {total}\n"
        f"✅ Получили доступ: {with_access}",
        reply_markup=admin_menu(),
    )


@router.callback_query(F.data == "admin:keywords")
async def admin_keywords(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    keywords = await get_all_keywords()
    if not keywords:
        await callback.message.edit_text(
            "Кодовых слов пока нет. Добавь первое!",
            reply_markup=admin_menu(),
        )
        return
    await callback.message.edit_text(
        "🔑 Кодовые слова (нажми чтобы удалить):",
        reply_markup=keywords_keyboard(keywords),
    )


@router.callback_query(F.data.startswith("admin:del:"))
async def admin_delete_keyword(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    word = callback.data.split(":", 2)[2]
    await delete_keyword(word)
    keywords = await get_all_keywords()
    if not keywords:
        await callback.message.edit_text(
            f"🗑 Слово «{word}» удалено.\n\nКодовых слов больше нет.",
            reply_markup=admin_menu(),
        )
        return
    await callback.message.edit_text(
        f"🗑 Слово «{word}» удалено.\n\n🔑 Оставшиеся слова:",
        reply_markup=keywords_keyboard(keywords),
    )


@router.callback_query(F.data == "admin:add_keyword")
async def admin_add_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AddKeyword.waiting_word)
    await callback.message.edit_text(
        "Введи кодовое слово, например: КУРС\n\n"
        "Пользователь должен будет написать именно это слово."
    )


@router.message(AddKeyword.waiting_word)
async def admin_got_word(message: Message, state: FSMContext):
    await state.update_data(word=message.text.strip())
    await state.set_state(AddKeyword.waiting_reward)
    await message.answer(
        "Теперь введи что получит пользователь — ссылку, текст или описание доступа.\n\n"
        "Например: https://t.me/+abcXYZ123"
    )


@router.message(AddKeyword.waiting_reward)
async def admin_got_reward(message: Message, state: FSMContext):
    data = await state.get_data()
    word = data["word"]
    reward = message.text.strip()
    await add_keyword(word, reward)
    await state.clear()
    await message.answer(
        f"✅ Кодовое слово добавлено!\n\n"
        f"🔑 Слово: <b>{word}</b>\n"
        f"🎁 Бонус: {reward}",
        parse_mode="HTML",
        reply_markup=admin_menu(),
    )


@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(Broadcast.waiting_message)
    await callback.message.edit_text(
        "Введи сообщение для рассылки всем пользователям.\n\n"
        "Отправь /cancel чтобы отменить."
    )


@router.message(Command("cancel"), Broadcast.waiting_message)
async def admin_broadcast_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Рассылка отменена.", reply_markup=admin_menu())


@router.message(Broadcast.waiting_message)
async def admin_broadcast_send(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    user_ids = await get_all_user_ids()
    sent, failed = 0, 0
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, message.text)
            sent += 1
        except Exception:
            failed += 1
    await message.answer(
        f"📢 Рассылка завершена!\n\n"
        f"✅ Доставлено: {sent}\n"
        f"❌ Не доставлено: {failed}",
        reply_markup=admin_menu(),
    )
