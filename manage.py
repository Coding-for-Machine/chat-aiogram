import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import requests
from decouple import config

TOKEN = config("TOKEN")
API_URL = config("API_URL")  # API manzilingizni qo'ying
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    phone_button = KeyboardButton(text='Telefon raqam yuborish 📱', request_contact=True)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[phone_button]],
        resize_keyboard=True, 
        one_time_keyboard=True
    )

    await message.answer(
        f"Assalomu alaykum! Telefon raqamingizni yuboring: {html.bold(message.from_user.full_name)}",
        reply_markup=keyboard
    )

@dp.message(lambda message: message.contact is not None)
async def handle_contact(message: Message):
    contact = message.contact
    
    user_data = {
        "phone_number": contact.phone_number,
        "telegram_id": message.from_user.id,
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name,
        "is_bot": message.from_user.is_bot,
        "language_code": message.from_user.language_code,
        "is_premium": getattr(message.from_user, 'is_premium', False),
        "registration_date": message.date.isoformat(),
        "contact_user_id": contact.user_id,
        "contact_first_name": contact.first_name,
        "contact_last_name": contact.last_name,
        "auth_data": str(message.date.timestamp())
    }

    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            API_URL,
            json=user_data,
            headers=headers,
            timeout=10
        )

        if response.status_code == 201:
            await message.answer("✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!")
            # Qo'shimcha keyboard yuborish
            menu = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📦 Buyurtmalarim")],
                    [KeyboardButton(text="ℹ️ Ma'lumot"), KeyboardButton(text="📞 Aloqa")]
                ],
                resize_keyboard=True
            )
            await message.answer("Quyidagi menyudan tanlang:", reply_markup=menu)
        else:
            error_msg = response.json().get('detail', 'Noma\'lum xato')
            await message.answer(f"⚠️ Xato: {error_msg}")

    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {str(e)}")
        await message.answer("🔌 Server bilan aloqada muammo. Iltimos keyinroq urinib ko'ring.")

@dp.message()
async def echo_handler(message: Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())