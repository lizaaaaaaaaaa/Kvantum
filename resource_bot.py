import logging
from aiogram import Bot, Dispatcher, executor, types
import sqlite3
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio
from prog import *
from parse import *
from token import token_resource_bot

tumbler = False

bot = Bot(token="")
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

class Search(StatesGroup):
    napr = State()
    theme = State()
    choose_post = State()

conn = sqlite3.connect("бот.db")

@dp.message_handler(commands="start")
async def cmd_test1(message: types.Message):
    await message.answer(f"Здравствуйте! Загляните в меню команд")

@dp.message_handler(commands="give_spisok")
async def start_add_resource(message: types.Message):
    cursor = conn.cursor()
    for napr in mas_group:
        spisok_name = [row for row in cursor.execute(f"Select name, secname from users where napr = '{napr}'")]
        mes = f"<strong>{napr}</strong>\n\n"
        for us in spisok_name:
            mes = mes + us[0] + " " + us [1] + "\n"
        await message.answer(f"{mes}", parse_mode="HTML")

@dp.message_handler(commands="add_resource")
async def start_add_resource(message: types.Message):
    await message.answer(f"Выберите направление", reply_markup=create_group())
    await Search.napr.set()

@dp.callback_query_handler(state=Search.napr)
async def choose_napr(call: types.CallbackQuery, state: FSMContext):
    action = call.data
    if action in mas_group:
        await state.update_data(napr = action)
        await call.message.answer("Введите тему поиска информации по выбранному направлению")
        await Search.theme.set()
    
@dp.message_handler(state=Search.theme)
async def enter_the(message: types.Message, state: FSMContext):
    await state.update_data(theme=message.text)
    data = await state.get_data()
    i = 0
    mas_link = []
    mas_title = []
    for title, link in get_post(data['theme']).items():
        mas_link.append(link)
        mas_title.append(title)
        i += 1
        await message.answer(f'{i}. <a href="{link}">{title}</a>', parse_mode='HTML')
    await state.update_data(links=mas_link)
    await state.update_data(titles=mas_title)
    await message.answer(f"Выбери номера статей", reply_markup=number())
    await Search.choose_post.set()

@dp.callback_query_handler(state=Search.choose_post)
async def choose_napr(call: types.CallbackQuery, state: FSMContext):
    action = call.data
    cursor = conn.cursor()
    data = await state.get_data()
    if int(action) in range(1, 21):
        poisk = [str(row[0]) for row in cursor.execute(f"Select id from posts where link = '{data['links'][int(action) - 1]}' and  data['napr']")]
        if poisk == []:
            request = [data['titles'][int(action) - 1], data['links'][int(action) - 1], data['napr']]
            cursor.execute(f"INSERT INTO posts (title, link, napr) VALUES (?, ?, ?);", request)  
            await call.message.answer(f"{data['titles'][int(action) - 1]}")
        else:
            await call.message.answer(f"Статья {action} уже выбрана")
    elif action == "21":
        await call.message.answer(f"Выбранные статьи будут направлены ученикам")
        await state.finish
    conn.commit()
    cursor.close()

def number():
    create_button = []
    for num in range(1, 21):
        create_button.append(types.InlineKeyboardButton(text=f"{num}", callback_data=f"{num}"))

    create_button.append(types.InlineKeyboardButton(text=f"Ок", callback_data=f"21"))
    keyboard = types.InlineKeyboardMarkup(row_width = 4)
    keyboard.add(*create_button)
    return keyboard

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)