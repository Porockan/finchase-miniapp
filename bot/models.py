import aiosqlite
from typing import List, Dict, Any, Optional
from .config import get_settings

settings = get_settings()


async def _dict_factory(cursor, row):
    """
    Преобразуем строки БД в словари {column: value}
    (так удобнее возвращать JSON через API).
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# ---------- ФУНКЦИИ ДЛЯ РАЗДЕЛОВ ----------

async def create_section(title: str, description: str, image_url: Optional[str]) -> int:
    async with aiosqlite.connect(settings.database_path) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        # order_num = максимальный + 1 (чтобы новые были в конце)
        cursor = await db.execute("SELECT COALESCE(MAX(order_num), 0) + 1 FROM sections;")
        (next_order,) = await cursor.fetchone()

        cursor = await db.execute(
            """
            INSERT INTO sections (title, description, image_url, order_num)
            VALUES (?, ?, ?, ?)
            """,
            (title, description, image_url, next_order),
        )
        await db.commit()
        return cursor.lastrowid


async def get_sections() -> List[Dict[str, Any]]:
    async with aiosqlite.connect(settings.database_path) as db:
        db.row_factory = _dict_factory
        await db.execute("PRAGMA foreign_keys = ON;")
        cursor = await db.execute(
            "SELECT id, title, description, image_url, order_num FROM sections ORDER BY order_num ASC, id ASC;"
        )
        rows = await cursor.fetchall()
        return rows


async def get_section(section_id: int) -> Optional[Dict[str, Any]]:
    async with aiosqlite.connect(settings.database_path) as db:
        db.row_factory = _dict_factory
        await db.execute("PRAGMA foreign_keys = ON;")
        cursor = await db.execute(
            "SELECT id, title, description, image_url, order_num FROM sections WHERE id = ?;",
            (section_id,),
        )
        row = await cursor.fetchone()
        return row


async def update_section_field(section_id: int, field: str, value: Any) -> None:
    if field not in ("title", "description", "image_url", "order_num"):
        raise ValueError("Нельзя изменять это поле")

    async with aiosqlite.connect(settings.database_path) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        await db.execute(f"UPDATE sections SET {field} = ? WHERE id = ?;", (value, section_id))
        await db.commit()


# ---------- ФУНКЦИИ ДЛЯ ПОДРАЗДЕЛОВ ----------

async def create_subsection(
    section_id: int, title: str, description: str, image_url: Optional[str]
) -> int:
    async with aiosqlite.connect(settings.database_path) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        cursor = await db.execute(
            "SELECT COALESCE(MAX(order_num), 0) + 1 FROM subsections WHERE section_id = ?;",
            (section_id,),
        )
        (next_order,) = await cursor.fetchone()

        cursor = await db.execute(
            """
            INSERT INTO subsections (section_id, title, description, image_url, order_num)
            VALUES (?, ?, ?, ?, ?)
            """,
            (section_id, title, description, image_url, next_order),
        )
        await db.commit()
        return cursor.lastrowid


async def get_subsections_by_section(section_id: int) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(settings.database_path) as db:
        db.row_factory = _dict_factory
        await db.execute("PRAGMA foreign_keys = ON;")
        cursor = await db.execute(
            """
            SELECT id, section_id, title, description, image_url, order_num
            FROM subsections
            WHERE section_id = ?
            ORDER BY order_num ASC, id ASC;
            """,
            (section_id,),
        )
        rows = await cursor.fetchall()
        return rows


async def get_subsection(subsection_id: int) -> Optional[Dict[str, Any]]:
    async with aiosqlite.connect(settings.database_path) as db:
        db.row_factory = _dict_factory
        await db.execute("PRAGMA foreign_keys = ON;")
        cursor = await db.execute(
            """
            SELECT id, section_id, title, description, image_url, order_num
            FROM subsections
            WHERE id = ?;
            """,
            (subsection_id,),
        )
        row = await cursor.fetchone()
        return row


async def update_subsection_field(subsection_id: int, field: str, value: Any) -> None:
    if field not in ("title", "description", "image_url", "order_num", "section_id"):
        raise ValueError("Нельзя изменять это поле")

    async with aiosqlite.connect(settings.database_path) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        await db.execute(f"UPDATE subsections SET {field} = ? WHERE id = ?;", (value, subsection_id))
        await db.commit()


# ---------- ФУНКЦИИ ДЛЯ МАТЕРИАЛОВ ----------

async def create_material(
    subsection_id: int,
    title: str,
    description: str,
    tg_link: Optional[str],
    image_url: Optional[str],
) -> int:
    async with aiosqlite.connect(settings.database_path) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        cursor = await db.execute(
            "SELECT COALESCE(MAX(order_num), 0) + 1 FROM materials WHERE subsection_id = ?;",
            (subsection_id,),
        )
        (next_order,) = await cursor.fetchone()

        cursor = await db.execute(
            """
            INSERT INTO materials (subsection_id, title, description, tg_link, image_url, order_num)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (subsection_id, title, description, tg_link, image_url, next_order),
        )
        await db.commit()
        return cursor.lastrowid


async def get_materials_by_subsection(subsection_id: int) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(settings.database_path) as db:
        db.row_factory = _dict_factory
        await db.execute("PRAGMA foreign_keys = ON;")
        cursor = await db.execute(
            """
            SELECT id, subsection_id, title, description, tg_link, image_url, order_num
            FROM materials
            WHERE subsection_id = ?
            ORDER BY order_num ASC, id ASC;
            """,
            (subsection_id,),
        )
        rows = await cursor.fetchall()
        return rows


async def update_material_field(material_id: int, field: str, value: Any) -> None:
    if field not in ("title", "description", "image_url", "order_num", "subsection_id", "tg_link"):
        raise ValueError("Нельзя изменять это поле")

    async with aiosqlite.connect(settings.database_path) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        await db.execute(f"UPDATE materials SET {field} = ? WHERE id = ?;", (value, material_id))
        await db.commit()


# ---------- СЛУЖЕБНЫЕ ФУНКЦИИ ДЛЯ СПИСКА ----------

async def get_full_tree() -> str:
    """
    Вернуть строку со всем деревом:
    разделы → подразделы → материалы.
    Удобно для команды /list.
    """
    async with aiosqlite.connect(settings.database_path) as db:
        await db.execute("PRAGMA foreign_keys = ON;")

        # Разделы
        db.row_factory = _dict_factory
        cursor = await db.execute(
            "SELECT id, title, description FROM sections ORDER BY order_num ASC, id ASC;"
        )
        sections = await cursor.fetchall()

        # Подразделы
        cursor = await db.execute(
            "SELECT id, section_id, title, description FROM subsections ORDER BY order_num ASC, id ASC;"
        )
        subsections = await cursor.fetchall()

        # Материалы
        cursor = await db.execute(
            "SELECT id, subsection_id, title, description, tg_link FROM materials ORDER BY order_num ASC, id ASC;"
        )
        materials = await cursor.fetchall()

    lines = []
    for s in sections:
        lines.append(f"Раздел #{s['id']}: {s['title']}")
        if s["description"]:
            lines.append(f"  Описание: {s['description']}")
        for sb in [x for x in subsections if x["section_id"] == s["id"]]:
            lines.append(f"  Подраздел #{sb['id']}: {sb['title']}")
            if sb["description"]:
                lines.append(f"    Описание: {sb['description']}")
            for m in [x for x in materials if x["subsection_id"] == sb["id"]]:
                line = f"    Материал #{m['id']}: {m['title']}"
                if m["tg_link"]:
                    line += f" (ссылка: {m['tg_link']})"
                lines.append(line)

    if not lines:
        return "База знаний пока пустая."
    return "\n".join(lines)