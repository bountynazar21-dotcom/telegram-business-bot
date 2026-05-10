from aiogram import Bot, Dispatcher
from aiogram.types import Message
from config import BOT_TOKEN
from answers import ANSWERS
from ai import ask_ai
from image_ai import generate_image_url
from db import init_db

import asyncio
from datetime import datetime

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Чати з активністю
active_chats = {}

# Затримка перед відповіддю
REPLY_DELAY = 1


def get_reply(text: str) -> str:
    text = text.lower()

    if "переміщення" in text:
        return ANSWERS["movement"]

    if any(word in text for word in ["графік", "розклад"]):
        return ANSWERS["schedule"]

    if any(word in text for word in ["терміново", "важливо"]):
        return ANSWERS["urgent"]

    return ANSWERS["unknown"]


def is_image_request(text: str) -> bool:
    text = text.lower()

    image_keywords = [
        "намалюй",
        "намалювати",
        "згенеруй картинку",
        "згенеруй фото",
        "створи картинку",
        "створи фото",
        "зроби картинку",
        "зроби фото",
        "картинку",
        "фото",
        "draw",
        "generate image",
        "create image",
        "make image"
    ]

    return any(word in text for word in image_keywords)


@dp.business_message()
async def handle_business_message(message: Message):

    if not message.text:
        return

    chat_id = message.chat.id
    business_id = message.business_connection_id

    if not business_id:
        print("Немає business_connection_id")
        return

    print(f"Нове повідомлення: {message.text}")

    message_time = datetime.now().timestamp()
    active_chats[chat_id] = message_time

    await asyncio.sleep(REPLY_DELAY)

    if active_chats.get(chat_id) != message_time:
        print("Чат оновився, бот мовчить")
        return

    # Генерація картинки
    if is_image_request(message.text):
        print("Запит на генерацію картинки")

        image_url = generate_image_url(message.text)

        await bot.send_photo(
            chat_id=chat_id,
            photo=image_url,
            caption="Готово 😅",
            business_connection_id=business_id
        )

        print("Картинку надіслано")
        return

    # AI відповідь
    ai_reply = ask_ai(chat_id, message.text)

    reply = ai_reply if ai_reply else get_reply(message.text)

    await bot.send_message(
        chat_id=chat_id,
        text=reply,
        business_connection_id=business_id
    )

    print("Автовідповідь надіслана")


async def main():
    init_db()
    print("Business AI bot запущений 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())