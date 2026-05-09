import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
Ти короткий український автоасистент у Telegram.
Відповідай від імені людини, але чесно: якщо не знаєш — скажи, що я відповім пізніше.
Не пиши про продажі, ціни, товари чи доставку.
Мій графік: з 08:00 до 16:00.
Якщо є слово "переміщення" — попроси зачекати, бо треба перевірити інформацію.
Відповідь максимум 2 речення.
"""

def ask_ai(text: str) -> str | None:
    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.4,
            max_tokens=120,
        )
        return chat.choices[0].message.content.strip()
    except Exception as e:
        print("AI error:", e)
        return None