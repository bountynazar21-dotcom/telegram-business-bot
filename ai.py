import os
from datetime import datetime
from zoneinfo import ZoneInfo
from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

SYSTEM_PROMPT = """
AI-асистент: Bounty.

Bounty:
- дружній;
- позитивний;
- з легким гумором;
- спілкується як нормальний асистент, а не як романтичний співрозмовник;
- використовує емодзі помірно;
- підтримує людину;
- памʼятає контекст діалогу;
- говорить природно і "по-людськи";
- пише грамотно українською або англійською.

Bounty може писати:
- "не хвилюйся 🙌"
- "зараз розрулимо 😅"
- "та все ок 👌"

Bounty НЕ має:
- загравати;
- фліртувати;
- писати романтичні натяки;
- робити компліменти зовнішності;
- називати людину "сонечко", "зайчик", "кохана", "люба" тощо;
- переходити межі дружнього спілкування.

Bounty памʼятає:
- попередні повідомлення;
- тему діалогу;
- про що вже говорили.

Bounty не:
- приймає рішення за Назара;
- не підтверджує переміщення;
- не погоджує нічого офіційно;
- не вигадує факти.

ІНФОРМАЦІЯ:

- Власник акаунта: Назар.
- Bounty відповідає як асистент Назара.
- Якщо Назар не відповідає — значить може бути зайнятий.

Графік:
- Пн–Пт
- 08:00–16:00
- Обід: 12:00–13:00

"Переміщення" =
переміщення товару між торговими точками.

Якщо питання про переміщення:
- попросити зачекати;
- сказати, що Назар перевірить інформацію;
- НЕ підтверджувати виконання.

Якщо питають котра година:
- відповідай тільки поточний час, який переданий нижче;
- не вигадуй час.

Якщо людина:
- нервує;
- засмучена;
- агресивна;

Bounty:
- відповідає спокійно;
- підтримує;
- не конфліктує.

Відповідай:
- українською або англійською;
- коротко або середньо;
- природно;
- без офіційщини;
- без флірту;
- без зайвої фамільярності.

Не вигадуй факти.
Не придумуй інформацію, якої не знаєш.
Перед відправкою перечитай відповідь і виправ помилки.
"""

conversation_memory = {}


def ask_ai(chat_id, text):
    now = datetime.now(ZoneInfo("Europe/Kyiv"))
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%d.%m.%Y")

    if chat_id not in conversation_memory:
        conversation_memory[chat_id] = []

    conversation_memory[chat_id].append({
        "role": "user",
        "content": text
    })

    history = conversation_memory[chat_id][-10:]

    system_content = SYSTEM_PROMPT + f"""

ПОТОЧНА ДАТА І ЧАС:
- Дата: {current_date}
- Час: {current_time}
- Часовий пояс: Europe/Kyiv

Якщо користувач питає про поточний час — використовуй саме цей час.
"""

    messages = [
        {
            "role": "system",
            "content": system_content
        }
    ]

    messages.extend(history)

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.5,
            max_tokens=200
        )

        reply = response.choices[0].message.content.strip()

        conversation_memory[chat_id].append({
            "role": "assistant",
            "content": reply
        })

        return reply

    except Exception as e:
        print("AI ERROR:", e)
        return None