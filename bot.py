from aiogram import Bot, Dispatcher
from aiogram.types import Message
from config import BOT_TOKEN
from answers import ANSWERS
from ai import ask_ai

import asyncio
from datetime import datetime

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Чати з активністю
active_chats = {}

# Затримка перед відповіддю
REPLY_DELAY = 120  # 2 хвилини


def get_reply(text: str) -> str:
    text = text.lower()

    if "переміщення" in text:
        return ANSWERS["movement"]

    if any(word in text for word in ["графік", "розклад"]):
        return ANSWERS["schedule"]

    if any(word in text for word in ["терміново", "важливо"]):
        return ANSWERS["urgent"]

    return ANSWERS["unknown"]


@dp.business_message()
async def handle_business_message(message: Message):

    if not message.text:
        return

    chat_id = message.chat.id
    business_id = message.business_connection_id

    print(f"Нове повідомлення: {message.text}")

    # Запам'ятовуємо час
    message_time = datetime.now().timestamp()
    active_chats[chat_id] = message_time

    # Чекаємо перед відповіддю
    await asyncio.sleep(REPLY_DELAY)

    # Якщо за цей час чат оновився
    if active_chats.get(chat_id) != message_time:
        print("Користувач уже отримав відповідь")
        return

    # AI відповідь
    ai_reply = ask_ai(message.text)

    # Якщо AI впав
    reply = ai_reply if ai_reply else get_reply(message.text)

    await bot.send_message(
        chat_id=chat_id,
        text=reply,
        business_connection_id=business_id
    )

    print("Автовідповідь надіслана")


async def main():
    print("Business AI bot запущений 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())