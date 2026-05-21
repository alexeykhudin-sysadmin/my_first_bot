import aiosqlite

DB_PATH = "bot.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                has_access INTEGER DEFAULT 0,
                last_keyword_at REAL DEFAULT 0
            )
        """)
        # Добавить колонку если база уже существует без неё
        try:
            await db.execute("ALTER TABLE users ADD COLUMN last_keyword_at REAL DEFAULT 0")
        except Exception:
            pass
        await db.execute("""
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE,
                reward TEXT,
                uses_count INTEGER DEFAULT 0
            )
        """)
        await db.commit()


async def add_user(telegram_id, username, first_name):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, username, first_name) VALUES (?, ?, ?)",
            (telegram_id, username, first_name),
        )
        await db.commit()


async def get_keyword(word):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id, word, reward, uses_count FROM keywords WHERE LOWER(word) = LOWER(?)",
            (word,),
        ) as cursor:
            return await cursor.fetchone()


async def set_user_access(telegram_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET has_access = 1 WHERE telegram_id = ?",
            (telegram_id,),
        )
        await db.commit()


async def increment_keyword_uses(word):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE keywords SET uses_count = uses_count + 1 WHERE LOWER(word) = LOWER(?)",
            (word,),
        )
        await db.commit()


async def add_keyword(word, reward):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO keywords (word, reward) VALUES (?, ?)",
            (word, reward),
        )
        await db.commit()


async def delete_keyword(word):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM keywords WHERE LOWER(word) = LOWER(?)",
            (word,),
        )
        await db.commit()


async def get_all_keywords():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT word, reward, uses_count FROM keywords"
        ) as cursor:
            return await cursor.fetchall()


async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            total = (await cursor.fetchone())[0]
        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE has_access = 1"
        ) as cursor:
            with_access = (await cursor.fetchone())[0]
        return total, with_access


async def get_user_has_access(telegram_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT has_access FROM users WHERE telegram_id = ?",
            (telegram_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return bool(row and row[0])


async def get_last_keyword_time(telegram_id: int) -> float:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT last_keyword_at FROM users WHERE telegram_id = ?",
            (telegram_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return float(row[0]) if row else 0.0


async def update_last_keyword_time(telegram_id: int, timestamp: float):
    async with aiosqlite.connect(DB_PATH) as db:
        # UPSERT — работает даже если пользователь не писал /start
        await db.execute(
            """INSERT INTO users (telegram_id, last_keyword_at)
               VALUES (?, ?)
               ON CONFLICT(telegram_id) DO UPDATE SET last_keyword_at = excluded.last_keyword_at""",
            (telegram_id, timestamp),
        )
        await db.commit()


async def get_all_user_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT telegram_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
