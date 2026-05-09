from aiogram import Bot, Dispatcher
from aiogram.types import Message
from config import BOT_TOKEN
from answers import ANSWERS
import asyncio

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def get_reply(text: str) -> str:
    text = text.lower()

    if any(word in text for word in ["привіт", "хай", "hello", "добрий", "доброго"]):
        return ANSWERS["greeting"]

    if any(word in text for word in ["графік", "розклад", "коли працюєш", "час роботи"]):
        return ANSWERS["schedule"]

    if any(word in text for word in ["переміщення", "перемістити", "перемістив", "переміщати"]):
        return ANSWERS["movement"]

    if any(word in text for word in ["терміново", "срочно", "важливо"]):
        return ANSWERS["urgent"]

    if any(word in text for word in ["дякую", "спасибі", "thanks"]):
        return ANSWERS["thanks"]

    return ANSWERS["unknown"]


@dp.business_message()
async def handle_business_message(message: Message):
    print("Business message:", message.text)

    if not message.text:
        return

    business_id = message.business_connection_id

    if not business_id:
        print("Немає business_connection_id")
        return

    reply = get_reply(message.text)

    await bot.send_message(
        chat_id=message.chat.id,
        text=reply,
        business_connection_id=business_id
    )


async def main():
    print("Business bot запущений 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())