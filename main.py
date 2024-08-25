import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Initialize bot and dispatcher
bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
dp = Dispatcher()

# Function to save request to JSON file
def save_request(user_id, message_text):
    try:
        with open('requests.json', 'r') as f:
            requests = json.load(f)
    except FileNotFoundError:
        requests = []

    new_request = {
        'order_number': f"#{len(requests) + 1}_{user_id}",
        'user_id': user_id,
        'message': message_text
    }

    requests.append(new_request)

    with open('requests.json', 'w') as f:
        json.dump(requests, f, indent=2)

# Create inline keyboard
send_request_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Send the request", callback_data="send_request")]
])

# Handle all messages
@dp.message()
async def handle_message(message: types.Message):
    await message.answer("Запрос зафиксирован", reply_markup=send_request_keyboard)

# Handle button press
@dp.callback_query(lambda c: c.data == 'send_request')
async def process_callback_send_request(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    message_text = callback_query.message.reply_to_message.text if callback_query.message.reply_to_message else "No message"

    # Save the request
    save_request(user_id, message_text)

    # Send confirmation message
    await bot.send_message(user_id, "Отправьте запрос")

async def main():
    # Start polling
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())