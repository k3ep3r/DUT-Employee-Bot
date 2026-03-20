import asyncio
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# --- НАСТРОЙКИ ---
TOKEN = os.getenv("TOKEN")
CHAT_ID = "@dut_minsk_mir"  # <-- замени на свой канал
ADMINS = [106945332]  # <-- вставь свой Telegram ID

STAFF = ["Мотор", "Слава", "ЛилКизил", "Слуцк", "Дима", "Андрей", "Артем"]

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_data = {}
user_state = {}

# --- ПРОВЕРКА ---
def is_admin(user_id):
    return user_id in ADMINS

# --- КНОПКИ ---
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏰ Время", callback_data="time")],
        [InlineKeyboardButton(text="💨 Чаша", callback_data="bowl")],
        [InlineKeyboardButton(text="🍹 Коктейли", callback_data="cocktail")],
        [InlineKeyboardButton(text="📄 Собрать", callback_data="build")]
    ])

def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Опубликовать", callback_data="confirm_publish")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_publish")]
    ])

def staff_kb(selected, prefix):
    buttons = []
    for name in STAFF:
        mark = "✅ " if name in selected else ""
        buttons.append([InlineKeyboardButton(
            text=mark + name,
            callback_data=f"{prefix}_{name}"
        )])

    buttons.append([InlineKeyboardButton(text="✔️ Готово", callback_data=f"{prefix}_done")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- ДАТА (без locale — работает везде) ---
def get_date():
    now = datetime.now()

    days = {
        "Monday": "понедельник",
        "Tuesday": "вторник",
        "Wednesday": "среда",
        "Thursday": "четверг",
        "Friday": "пятница",
        "Saturday": "суббота",
        "Sunday": "воскресенье"
    }

    months = {
        "January": "января",
        "February": "февраля",
        "March": "марта",
        "April": "апреля",
        "May": "мая",
        "June": "июня",
        "July": "июля",
        "August": "августа",
        "September": "сентября",
        "October": "октября",
        "November": "ноября",
        "December": "декабря"
    }

    day = days[now.strftime("%A")]
    month = months[now.strftime("%B")]

    return f"Сегодня {now.day} {month}, {day} 🌸"

# --- СБОРКА ПОСТА ---
def build_post(data):
    return f"""
{get_date()}

Работаем с {data.get("time", "??")}

Сегодня на смене😍

Забьют самую сочную и яркую чашу:
{", ".join(data.get("bowl", []))}

Удивят неповторимыми коктейлями:
{", ".join(data.get("cocktail", []))}

Для бронирования столов можете написать нам в личные сообщения:
https://t.me/DUT_MINSK_MIR

Или набрать по номеру телефона:
+375-29-134-06-06

Будем рады вас видеть по адресу: Братская 6А❤️
"""

# --- START ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    if not is_admin(msg.from_user.id):
        await msg.answer("Нет доступа ❌")
        return

    user_data[msg.from_user.id] = {
        "bowl": [],
        "cocktail": []
    }

    await msg.answer("Настрой пост 👇", reply_markup=main_menu())

# --- ВРЕМЯ ---
@dp.callback_query(lambda c: c.data == "time")
async def time(call: types.CallbackQuery):
    user_state[call.from_user.id] = "time"
    await call.message.answer("Введи время (пример: 12:00-23:00)")

@dp.message()
async def input_handler(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return

    if user_state.get(msg.from_user.id) == "time":
        user_data[msg.from_user.id]["time"] = msg.text
        await msg.answer("Сохранил ✅", reply_markup=main_menu())

# --- ЧАША ---
@dp.callback_query(lambda c: c.data == "bowl")
async def bowl(call: types.CallbackQuery):
    selected = user_data[call.from_user.id]["bowl"]
    await call.message.answer("Кто делает чашу?",
                              reply_markup=staff_kb(selected, "bowl"))

@dp.callback_query(lambda c: c.data.startswith("bowl_"))
async def bowl_select(call: types.CallbackQuery):
    name = call.data.split("_")[1]

    if name == "done":
        await call.message.answer("Сохранил ✅", reply_markup=main_menu())
        return

    selected = user_data[call.from_user.id]["bowl"]

    if name in selected:
        selected.remove(name)
    else:
        if len(selected) < 3:
            selected.append(name)

    await call.message.edit_reply_markup(reply_markup=staff_kb(selected, "bowl"))

# --- КОКТЕЙЛИ ---
@dp.callback_query(lambda c: c.data == "cocktail")
async def cocktail(call: types.CallbackQuery):
    selected = user_data[call.from_user.id]["cocktail"]
    await call.message.answer("Кто делает коктейли?",
                              reply_markup=staff_kb(selected, "cocktail"))

@dp.callback_query(lambda c: c.data.startswith("cocktail_"))
async def cocktail_select(call: types.CallbackQuery):
    name = call.data.split("_")[1]

    if name == "done":
        await call.message.answer("Сохранил ✅", reply_markup=main_menu())
        return

    selected = user_data[call.from_user.id]["cocktail"]

    if name in selected:
        selected.remove(name)
    else:
        if len(selected) < 3:
            selected.append(name)

    await call.message.edit_reply_markup(reply_markup=staff_kb(selected, "cocktail"))

# --- ПРЕВЬЮ ---
@dp.callback_query(lambda c: c.data == "build")
async def build(call: types.CallbackQuery):
    data = user_data[call.from_user.id]
    post = build_post(data)

    user_data[call.from_user.id]["preview"] = post

    await call.message.answer("Вот пост 👇")
    await call.message.answer(post, reply_markup=confirm_kb())

# --- ПУБЛИКАЦИЯ ---
@dp.callback_query(lambda c: c.data == "confirm_publish")
async def confirm_publish(call: types.CallbackQuery):
    post = user_data[call.from_user.id].get("preview")

    if not post:
        await call.message.answer("Сначала собери пост ❌")
        return

    await bot.send_message(chat_id=CHAT_ID, text=post)
    await call.message.answer("Опубликовано ✅🔥")

# --- ОТМЕНА ---
@dp.callback_query(lambda c: c.data == "cancel_publish")
async def cancel_publish(call: types.CallbackQuery):
    await call.message.answer("Отменено ❌", reply_markup=main_menu())

# --- ЗАПУСК (FIX CONFLICT) ---
async def main():
    print("RESET WEBHOOK...")
    await bot.delete_webhook(drop_pending_updates=True)

    print("START POLLING...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
