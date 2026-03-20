import asyncio
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

# --- CONFIG ---
TOKEN = os.getenv("TOKEN")
CHAT_ID = "@dut_minsk_mir"
SUPER_ADMIN = 106945332  # <-- твой ID

KM_STAFF = ["Дмитрий 🏍", "Вячеслав  🤙🏽", "Никита", "Владислав"]
BAR_STAFF = ["Андрей 🥷", "Андрей", "Дмитрий 🍰", "Артём 🍹"]

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode="HTML",
        link_preview_is_disabled=True
    )
)

dp = Dispatcher()

user_data = {}
users = set()  # <-- все пользователи
pending_admin = {}

# --- ADMINS (Railway) ---
def get_admins():
    raw = os.getenv("ADMINS", "")
    return set(int(x) for x in raw.split(",") if x)


def save_admins(admins):
    return ",".join(map(str, admins))


def is_admin(user_id):
    return user_id in get_admins() or user_id == SUPER_ADMIN

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

🍹 <b>Удивят неповторимыми коктейлями:</b>
{", ".join(data.get("bar", []))}

📩 https://t.me/DUT_MINSK_MIR
📞 +375-29-134-06-06

📍 Братская 6А❤️
"""

# --- UI ---
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
        [
            InlineKeyboardButton(text="💨 КМ", callback_data="km"),
            InlineKeyboardButton(text="🍹 Бар", callback_data="bar")
        ],
        [InlineKeyboardButton(text="📄 Сделать пост", callback_data="build")],
        [InlineKeyboardButton(text="👑 Админы", callback_data="admin_menu")],
        [InlineKeyboardButton(text="🔄 Сброс", callback_data="reset")]
    ])


def get_admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить", callback_data="add_admin_ui")],
        [InlineKeyboardButton(text="➖ Удалить", callback_data="remove_admin_ui")],
        [InlineKeyboardButton(text="👥 Список", callback_data="list_admins")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])


def staff_kb(staff_list, selected, prefix):
    buttons = []

    for name in staff_list:
        mark = "✅ " if name in selected else ""
        buttons.append([
            InlineKeyboardButton(text=mark + name, callback_data=f"{prefix}_{name}")
        ])

    buttons.append([InlineKeyboardButton(text="✔️ Готово", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_select_kb(current_admins, mode):
    buttons = []

    for user_id in users:
        mark = "✅ " if user_id in current_admins else ""
        buttons.append([
            InlineKeyboardButton(
                text=f"{mark}{user_id}",
                callback_data=f"{mode}_{user_id}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(text="✔️ Готово", callback_data="admin_done")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def update_menu(call):
    await call.message.edit_text(
        get_main_text(call.from_user.id),
        reply_markup=get_main_kb()
    )

# --- START ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    users.add(msg.from_user.id)

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
        [InlineKeyboardButton(text="12:00 до 02:00", callback_data="time_1")],
        [InlineKeyboardButton(text="12:00 до 04:00", callback_data="time_2")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])

    await call.message.edit_text("Выбери время:", reply_markup=kb)


@dp.callback_query(lambda c: c.data.startswith("time_"))
async def time_select(call: types.CallbackQuery):
    if call.data == "time_1":
        user_data[call.from_user.id]["time"] = "12:00 до 02:00"
    elif call.data == "time_2":
        user_data[call.from_user.id]["time"] = "12:00 до 04:00""

    await update_menu(call)

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

# --- ADMIN UI ---
@dp.callback_query(lambda c: c.data == "admin_menu")
async def admin_menu(call: types.CallbackQuery):
    if call.from_user.id != SUPER_ADMIN:
        return await call.answer("Нет доступа ❌", show_alert=True)

    await call.message.edit_text(
        "👑 Управление администраторами:",
        reply_markup=get_admin_kb()
    )


@dp.callback_query(lambda c: c.data == "add_admin_ui")
async def add_admin_ui(call: types.CallbackQuery):
    admins = get_admins()

    await call.message.edit_text(
        "➕ Выбери админов:",
        reply_markup=admin_select_kb(admins, "addadmin")
    )


@dp.callback_query(lambda c: c.data == "remove_admin_ui")
async def remove_admin_ui(call: types.CallbackQuery):
    admins = get_admins()

    await call.message.edit_text(
        "➖ Убери админов:",
        reply_markup=admin_select_kb(admins, "deladmin")
    )


@dp.callback_query(lambda c: c.data.startswith("addadmin_"))
async def add_admin_click(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    admins = get_admins()

    admins.add(user_id)
    new_value = save_admins(admins)

    await call.answer("Добавлен ✅")

    await call.message.edit_reply_markup(
        reply_markup=admin_select_kb(admins, "addadmin")
    )

    print("ADMINS =", new_value)


@dp.callback_query(lambda c: c.data.startswith("deladmin_"))
async def del_admin_click(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    admins = get_admins()

    if user_id == SUPER_ADMIN:
        return await call.answer("Нельзя ❌", show_alert=True)

    admins.discard(user_id)
    new_value = save_admins(admins)

    await call.answer("Удален ❌")

    await call.message.edit_reply_markup(
        reply_markup=admin_select_kb(admins, "deladmin")
    )

    print("ADMINS =", new_value)


@dp.callback_query(lambda c: c.data == "admin_done")
async def admin_done(call: types.CallbackQuery):
    admins = get_admins()

    await call.message.edit_text(
        "Скопируй и вставь в Railway:\n\n"
        f"<code>{','.join(map(str, admins))}</code>",
        reply_markup=get_admin_kb()
    )


@dp.callback_query(lambda c: c.data == "list_admins")
async def list_admins(call: types.CallbackQuery):
    admins = get_admins()

    text = "👥 Админы:\n\n"
    for a in admins:
        text += f"• {a}\n"

    await call.message.edit_text(text, reply_markup=get_admin_kb())

# --- COMMON ---
@dp.callback_query(lambda c: c.data == "back")
async def back(call: types.CallbackQuery):
    await update_menu(call)


@dp.callback_query(lambda c: c.data == "reset")
async def reset(call: types.CallbackQuery):
    user_data[call.from_user.id] = {
        "time": None,
        "km": [],
        "bar": []
    }
    await update_menu(call)


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

# --- RUN ---
async def main():
    print("RESET WEBHOOK...")
    await bot.delete_webhook(drop_pending_updates=True)

    print("START POLLING...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
