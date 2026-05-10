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
                    user_id TEXT,
                    username TEXT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    chat_id TEXT PRIMARY KEY,
                    name TEXT,
                    username TEXT,
                    language TEXT DEFAULT 'uk',
                    tone TEXT DEFAULT 'friendly',
                    notes TEXT,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id SERIAL PRIMARY KEY,
                    category TEXT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    priority INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS examples (
                    id SERIAL PRIMARY KEY,
                    user_question TEXT NOT NULL,
                    good_answer TEXT NOT NULL,
                    bad_answer TEXT,
                    topic TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_topics (
                    id SERIAL PRIMARY KEY,
                    chat_id TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    summary TEXT,
                    status TEXT DEFAULT 'active',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    chat_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'new',
                    priority TEXT DEFAULT 'normal',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)


def save_message(chat_id, role, content, user_id=None, username=None):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO messages (chat_id, user_id, username, role, content, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (str(chat_id), user_id, username, role, content, datetime.now()))


def get_recent_messages(chat_id, limit=10):
    with connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT role, content
                FROM messages
                WHERE chat_id = %s
                ORDER BY id DESC
                LIMIT %s
            """, (str(chat_id), limit))

            rows = cur.fetchall()

    return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]


def upsert_contact(chat_id, name=None, username=None, language="uk", tone="friendly"):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO contacts (chat_id, name, username, language, tone, last_seen)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (chat_id)
                DO UPDATE SET
                    name = COALESCE(EXCLUDED.name, contacts.name),
                    username = COALESCE(EXCLUDED.username, contacts.username),
                    language = COALESCE(EXCLUDED.language, contacts.language),
                    tone = COALESCE(EXCLUDED.tone, contacts.tone),
                    last_seen = EXCLUDED.last_seen;
            """, (str(chat_id), name, username, language, tone, datetime.now()))


def get_contact(chat_id):
    with connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT *
                FROM contacts
                WHERE chat_id = %s
            """, (str(chat_id),))

            return cur.fetchone()


def add_knowledge(category, title, content, priority=1):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO knowledge (category, title, content, priority, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (category, title, content, priority, datetime.now()))


def get_knowledge(limit=20):
    with connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT category, title, content, priority
                FROM knowledge
                ORDER BY priority DESC, id DESC
                LIMIT %s
            """, (limit,))

            return cur.fetchall()


def add_example(user_question, good_answer, bad_answer=None, topic=None):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO examples (user_question, good_answer, bad_answer, topic, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_question, good_answer, bad_answer, topic, datetime.now()))


def get_examples(limit=10):
    with connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT user_question, good_answer, bad_answer, topic
                FROM examples
                ORDER BY id DESC
                LIMIT %s
            """, (limit,))

            return cur.fetchall()


def set_chat_topic(chat_id, topic, summary=None, status="active"):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO chat_topics (chat_id, topic, summary, status, updated_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (str(chat_id), topic, summary, status, datetime.now()))


def get_chat_topics(chat_id, limit=5):
    with connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT topic, summary, status, updated_at
                FROM chat_topics
                WHERE chat_id = %s
                ORDER BY updated_at DESC
                LIMIT %s
            """, (str(chat_id), limit))

            return cur.fetchall()


def add_task(chat_id, title, description=None, priority="normal"):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tasks (chat_id, title, description, priority, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (str(chat_id), title, description, priority, "new", datetime.now()))


def get_tasks(chat_id=None, status="new", limit=10):
    with connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if chat_id:
                cur.execute("""
                    SELECT *
                    FROM tasks
                    WHERE chat_id = %s AND status = %s
                    ORDER BY id DESC
                    LIMIT %s
                """, (str(chat_id), status, limit))
            else:
                cur.execute("""
                    SELECT *
                    FROM tasks
                    WHERE status = %s
                    ORDER BY id DESC
                    LIMIT %s
                """, (status, limit))

            return cur.fetchall()