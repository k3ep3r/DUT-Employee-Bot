import asyncio
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# --- CONFIG ---
TOKEN = os.getenv("TOKEN")
CHAT_ID = "@dut_minsk_mir"  # <-- замени
ADMINS = [106945332]  # <-- вставь свой ID

KM_STAFF = ["Мотор", "Вячеслав", "Никита", "Владислав"]
BAR_STAFF = ["Андрей", "Андрей", "Дима", "Артём"]

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()

user_data = {}

# --- ADMIN CHECK ---
def is_admin(user_id):
    return user_id in ADMINS

# --- DATE ---
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

    return f"Сегодня {now.day} {months[now.strftime('%B')]}, {days[now.strftime('%A')]} 🌸"

# --- POST ---
def build_post(data):
    return f"""
<b>{get_date()}</b>

<b>Работаем с {data.get("time", "??")}</b>

Сегодня на смене😍

💨 <b>Забьют самую сочную и яркую чашу:</b>
{", ".join(data.get("km", []))}

🍹 <b>Удивят неповторимыми, авторскими, коктейлями:</b>
{", ".join(data.get("bar", []))}

Для бронирования столов можете написать нам в личные сообщения:
📩 https://t.me/DUT_MINSK_MIR
Или набрать по номеру телефона:
📞 +375-29-134-06-06
Будем рады вас видеть по адресу:
📍 Братская 6А ❤️
"""

# --- MAIN UI ---
def get_main_text(user_id):
    data = user_data.get(user_id, {})

    return (
        f"⏰ Время: {data.get('time', 'не выбрано')}\n"
        f"💨 КМ: {', '.join(data.get('km', [])) or '—'}\n"
        f"🍹 Бар: {', '.join(data.get('bar', [])) or '—'}"
    )

def get_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏰ Время", callback_data="time")],
        [InlineKeyboardButton(text="💨 КМ", callback_data="km")],
        [InlineKeyboardButton(text="🍹 Бар", callback_data="bar")],
        [InlineKeyboardButton(text="📄 Собрать", callback_data="build")],
        [InlineKeyboardButton(text="🔄 Сброс", callback_data="reset")]
    ])

async def update_menu(call):
    await call.message.edit_text(
        get_main_text(call.from_user.id),
        reply_markup=get_main_kb()
    )

# --- START ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return await msg.answer("Нет доступа ❌")

    user_data[msg.from_user.id] = {
        "time": None,
        "km": [],
        "bar": []
    }

    await msg.answer(
        get_main_text(msg.from_user.id),
        reply_markup=get_main_kb()
    )

# --- TIME ---
@dp.callback_query(lambda c: c.data == "time")
async def time(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="12:00–23:00", callback_data="time_1")],
        [InlineKeyboardButton(text="14:00–02:00", callback_data="time_2")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])

    await call.message.edit_text("Выбери время:", reply_markup=kb)

@dp.callback_query(lambda c: c.data.startswith("time_"))
async def time_select(call: types.CallbackQuery):
    if call.data == "time_1":
        user_data[call.from_user.id]["time"] = "12:00–23:00"
    elif call.data == "time_2":
        user_data[call.from_user.id]["time"] = "14:00–02:00"

    await update_menu(call)

# --- STAFF KB ---
def staff_kb(staff_list, selected, prefix):
    buttons = []

    for name in staff_list:
        mark = "✅ " if name in selected else ""
        buttons.append([
            InlineKeyboardButton(text=mark + name, callback_data=f"{prefix}_{name}")
        ])

    buttons.append([InlineKeyboardButton(text="✔️ Готово", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- KM ---
@dp.callback_query(lambda c: c.data == "km")
async def km(call: types.CallbackQuery):
    await call.message.edit_text(
        "Выбери КМ:",
        reply_markup=staff_kb(KM_STAFF, user_data[call.from_user.id]["km"], "km")
    )

@dp.callback_query(lambda c: c.data.startswith("km_"))
async def km_select(call: types.CallbackQuery):
    name = call.data.split("_")[1]
    selected = user_data[call.from_user.id]["km"]

    if name in selected:
        selected.remove(name)
    else:
        if len(selected) < 3:
            selected.append(name)

    await call.message.edit_reply_markup(
        reply_markup=staff_kb(KM_STAFF, selected, "km")
    )

# --- BAR ---
@dp.callback_query(lambda c: c.data == "bar")
async def bar(call: types.CallbackQuery):
    await call.message.edit_text(
        "Выбери Бар:",
        reply_markup=staff_kb(BAR_STAFF, user_data[call.from_user.id]["bar"], "bar")
    )

@dp.callback_query(lambda c: c.data.startswith("bar_"))
async def bar_select(call: types.CallbackQuery):
    name = call.data.split("_")[1]
    selected = user_data[call.from_user.id]["bar"]

    if name in selected:
        selected.remove(name)
    else:
        if len(selected) < 3:
            selected.append(name)

    await call.message.edit_reply_markup(
        reply_markup=staff_kb(BAR_STAFF, selected, "bar")
    )

# --- BACK ---
@dp.callback_query(lambda c: c.data == "back")
async def back(call: types.CallbackQuery):
    await update_menu(call)

# --- RESET ---
@dp.callback_query(lambda c: c.data == "reset")
async def reset(call: types.CallbackQuery):
    user_data[call.from_user.id] = {
        "time": None,
        "km": [],
        "bar": []
    }
    await update_menu(call)

# --- BUILD ---
@dp.callback_query(lambda c: c.data == "build")
async def build(call: types.CallbackQuery):
    data = user_data[call.from_user.id]

    if not data.get("time"):
        return await call.answer("Выбери время ❌", show_alert=True)

    post = build_post(data)

    await call.message.answer("Пост 👇")
    await call.message.answer(post)

    await bot.send_message(chat_id=CHAT_ID, text=post)
    await call.message.answer("Опубликовано ✅🔥")

# --- START BOT ---
async def main():
    print("RESET WEBHOOK...")
    await bot.delete_webhook(drop_pending_updates=True)

    print("START POLLING...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
