import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")


def connect():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    chat_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS learned_answers (
                    id SERIAL PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)


def save_message(chat_id, role, content):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO messages (chat_id, role, content, created_at)
                VALUES (%s, %s, %s, %s)
                """,
                (str(chat_id), role, content, datetime.now())
            )


def get_recent_messages(chat_id, limit=10):
    with connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT role, content
                FROM messages
                WHERE chat_id = %s
                ORDER BY id DESC
                LIMIT %s
                """,
                (str(chat_id), limit)
            )

            rows = cur.fetchall()

    return [
        {"role": row["role"], "content": row["content"]}
        for row in reversed(rows)
    ]


def save_learned_answer(question, answer):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO learned_answers (question, answer, created_at)
                VALUES (%s, %s, %s)
                """,
                (question, answer, datetime.now())
            )


def get_learned_answers(limit=20):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT question, answer
                FROM learned_answers
                ORDER BY id DESC
                LIMIT %s
                """,
                (limit,)
            )

            return cur.fetchall()