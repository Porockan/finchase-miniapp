import aiosqlite
from .config import get_settings

settings = get_settings()


async def init_db() -> None:
    """
    Создаём таблицы, если их ещё нет.
    Функция вызывается один раз при старте бота.
    """
    async with aiosqlite.connect(settings.database_path) as db:
        # Включаем внешние ключи (FOREIGN KEY)
        await db.execute("PRAGMA foreign_keys = ON;")

        # Таблица разделов
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                image_url TEXT,
                order_num INTEGER NOT NULL DEFAULT 0
            );
            """
        )

        # Таблица подразделов
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS subsections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                section_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                image_url TEXT,
                order_num INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE CASCADE
            );
            """
        )

        # Таблица материалов
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subsection_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                tg_link TEXT,
                image_url TEXT,
                order_num INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (subsection_id) REFERENCES subsections(id) ON DELETE CASCADE
            );
            """
        )

        await db.commit()