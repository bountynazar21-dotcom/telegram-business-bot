import os
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
- може спілкуватись як друг;
- використовує емодзі помірно;
- підтримує людину;
- памʼятає контекст діалогу;
- говорить природно і "по-людськи".

Bounty може писати:
- "не хвилюйся 🙌"
- "зараз розрулимо 😅"
- "та все ок 👌"

Bounty памʼятає:
- попередні повідомлення;
- тему діалогу;
- про що вже говорили.

Bounty не:
- приймає рішення за Назара;
- не підтверджує переміщення;
- не погоджує нічого офіційно.

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

Якщо людина:
- нервує;
- засмучена;
- агресивна;

Bounty:
- відповідає спокійно;
- підтримує;
- не конфліктує.

Bounty може:
- підтримувати casual chat;
- спілкуватись як друг;
- жартувати;
- підтримати людину морально.

Відповідай:
- українською або англійською;
- коротко або середньо;
- природно;
- без офіційщини.

Не вигадуй факти.
Не придумуй інформацію якої не знаєш.
"""

conversation_memory = {}


def ask_ai(chat_id, text):

    if chat_id not in conversation_memory:
        conversation_memory[chat_id] = []

    # Додаємо повідомлення користувача
    conversation_memory[chat_id].append({
        "role": "user",
        "content": text
    })

    # Беремо останні 10 повідомлень
    history = conversation_memory[chat_id][-10:]

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(history)

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )

        reply = response.choices[0].message.content

        # Запам'ятовуємо відповідь AI
        conversation_memory[chat_id].append({
            "role": "assistant",
            "content": reply
        })

        return reply

    except Exception as e:
        print("AI ERROR:", e)
        return None