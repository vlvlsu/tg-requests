import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Form(StatesGroup):
    waiting_for_request = State()

def save_request(user_id, message_text):
    try:
        with open('requests.json', 'r', encoding='utf-8') as f:
            requests = json.load(f)
    except FileNotFoundError:
        requests = []

    new_request = {
        'order_number': f"#{len(requests) + 1}_{user_id}",
        'user_id': user_id,
        'message': message_text
    }

    requests.append(new_request)

    with open('requests.json', 'w', encoding='utf-8') as f:
        json.dump(requests, f, ensure_ascii=False, indent=2)

send_request_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Отправить сообщение")]],
    resize_keyboard=True
)

async def delete_message_later(chat_id: int, message_id: int):
    await asyncio.sleep(60)  # Wait for 60 seconds
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

@dp.message(Command("start"))
async def start_command(message: types.Message):
    response = await message.answer("Здесь можно отправить сообщение лапчику", reply_markup=send_request_keyboard)
    asyncio.create_task(delete_message_later(message.chat.id, message.message_id))
    asyncio.create_task(delete_message_later(response.chat.id, response.message_id))

@dp.message(F.text == "Отправить сообщение")
async def handle_send_request(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_request)
    response = await message.answer("Напишите ваш запрос", reply_markup=ReplyKeyboardRemove())
    asyncio.create_task(delete_message_later(message.chat.id, message.message_id))
    asyncio.create_task(delete_message_later(response.chat.id, response.message_id))

@dp.message(Form.waiting_for_request)
async def handle_request(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    request_text = message.text

    save_request(user_id, request_text)

    await state.clear()
    response = await message.answer("🥰 Запрос улетел", reply_markup=send_request_keyboard)
    asyncio.create_task(delete_message_later(message.chat.id, message.message_id))
    asyncio.create_task(delete_message_later(response.chat.id, response.message_id))

@dp.message()
async def handle_other_messages(message: types.Message):
    response = await message.answer("Чтобы отправить сообщение, нажмите кнопку 'Отправить сообщение'", reply_markup=send_request_keyboard)
    asyncio.create_task(delete_message_later(message.chat.id, message.message_id))
    asyncio.create_task(delete_message_later(response.chat.id, response.message_id))

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())