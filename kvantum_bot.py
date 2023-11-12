import logging
from aiogram import Bot, Dispatcher, executor, types
import sqlite3
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio

tumbler = False

bot = Bot(token="5927658024:AAF_HnJzTi4tCnHmiY7BnAEKbAE-HELLxgc")
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

conn = sqlite3.connect("бот.db")

answer_quiz = ['Мне было интересно, я этого не знал/а', 'Я это итак знаю', 'Мне это неинтересно', 'Я не смотрел']
cursor = conn.cursor()   
mas_group = [str(row[0]) for row in cursor.execute("Select name from NAPRAVLENIYA")]
conn.commit()
cursor.close()

@dp.message_handler(commands="start")
async def cmd_test1(message: types.Message):
    cursor = conn.cursor()    
    get_napr = [str(row[0]) for row in cursor.execute(f"Select napr from users where id = '{message.from_user.id}';")]
    print(get_napr)
    conn.commit()
    cursor.close()
    if get_napr == []:
        await message.answer(f"👨‍💻 Здравствуй! Выбери направление, на котором ты обучаешься:", reply_markup=create_group())
    else:
        await message.answer(f"👨‍💻 Здравствуй! Ты уже был ранее зарегестрирован на направлении {get_napr[0]}")
        await message.answer("Поздравляю, теперь ты снова регулярно будешь получать интересную и нужную информацию по своему направлению и 🧠#качатьмозги!")

@dp.poll_answer_handler()
async def handle_poll_answer(quiz_answer: types.PollAnswer):
    cursor = conn.cursor()   
    try:
        for ans in answer_quiz:
            if answer_quiz.index(ans) == quiz_answer.option_ids[0]:
                answer = ans
        zapis_quiz = [quiz_answer.user.id, str(answer)]
        print(zapis_quiz)
        cursor.execute(f'INSERT INTO answer_quiz (id_user, answer) VALUES (?, ?);', zapis_quiz)
        conn.commit()
        cursor.close()  
    except IndexError:
        print(f'Пользователь {quiz_answer.user.id} отменил голос')

async def rassylka():
    while True:
        try:
            for napr in mas_group:
                cursor = conn.cursor()
                list_users = [str(row[0]) for row in cursor.execute(f"Select id from users where napr = '{napr}'")]
                title = [str(row[0]) for row in cursor.execute(f"Select title from posts where napr = '{napr}' limit 1;")]
                link = [str(row[0]) for row in cursor.execute(f"Select link from posts where napr = '{napr}' limit 1;")]
                id_post = [str(row[0]) for row in cursor.execute(f"Select id from posts where napr = '{napr}' limit 1;")]

                cursor.execute(f"delete from posts where id = {id_post[0]}")

                conn.commit()
                cursor.close()     

                for i in list_users:
                    await bot.send_message(f'{i}', f'<a href="{link[0]}">{title[0]}</a>', parse_mode='HTML')
            await asyncio.sleep(15)
        except IndexError:
                print("Посты кончились!")

async def on_startup(dp):
    asyncio.create_task(rassylka())  

@dp.message_handler(commands="subject")
async def subject(message: types.Message):
    try:
        cursor = conn.cursor()
        napr = [str(row[0]) for row in cursor.execute(f"select napr from users where id = '{message.from_user.id}'")]
        conn.commit()
        cursor.close()  

        await message.answer(f"Твоё направление <strong>{napr[0]}</strong>", parse_mode='HTML')
    except IndexError:
        await message.answer(f"Ты ещё не выбрал направление!")

@dp.message_handler(commands="change_subjects")
async def change_subject(message: types.Message):
    try:
        cursor = conn.cursor()
        cursor.execute(f"delete from users where id = {message.from_user.id}")
        conn.commit()
        cursor.close()  

        await message.answer(f"Выбери направление, на котором ты обучаешься:", reply_markup=create_group())
    except:
        await message.answer(f"Ты ещё не выбрал направление!")
    
@dp.callback_query_handler()
async def action(call: types.CallbackQuery):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    action = call.data
    cursor = conn.cursor()

    if action in mas_group:
        data = (call.from_user.id, call.from_user.first_name, call.from_user.last_name, action)
        cursor.execute(f"INSERT INTO users (id, name, secname, napr) VALUES (?, ?, ?, ?);", data)  

        await call.message.answer(f"Поздравляю, теперь ты регулярно будешь получать интересную информацию по направлению {action} и 🧠#качатьмозги!")
    conn.commit()
    cursor.close() 

def create_group():
    create_buttons = []
    for elem in mas_group:
        create_buttons.append(types.InlineKeyboardButton(text=f"{elem}", callback_data=f"{elem}"))

    keyboard = types.InlineKeyboardMarkup(row_width = 1)
    keyboard.add(*create_buttons)
    return keyboard

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)