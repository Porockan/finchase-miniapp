from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.fsm.context import FSMContext

from .config import get_settings
from . import models
from .admin import (
    AddSectionStates,
    AddSubsectionStates,
    AddMaterialStates,
    EditStates,
)

router = Router()
settings = get_settings()


def is_admin(message: Message) -> bool:
    """
    Проверяем, что команду выполняет админ.
    """
    return message.from_user and message.from_user.id == settings.admin_chat_id


# ---------- /start ----------

@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Команда /start — показывает кнопку открытия Mini App.
    """
    from aiogram.types import WebAppInfo

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="Открыть базу знаний",
                    web_app=WebAppInfo(url=settings.webapp_url),
                )
            ]
        ],
        resize_keyboard=True,
    )

    await message.answer(
        "Привет! Это база знаний агентства недвижимости.\n"
        "Нажмите кнопку ниже, чтобы открыть Mini App.",
        reply_markup=kb,
    )


# ---------- /list ----------

@router.message(Command("list"))
async def cmd_list(message: Message):
    if not is_admin(message):
        await message.answer("Эта команда только для администратора.")
        return

    tree_text = await models.get_full_tree()
    # Если текст длинный, Telegram сам разобьёт на части
    await message.answer(tree_text)


# ---------- /add_section ----------

@router.message(Command("add_section"))
async def cmd_add_section(message: Message, state: FSMContext):
    if not is_admin(message):
        await message.answer("Эта команда только для администратора.")
        return

    await state.set_state(AddSectionStates.waiting_for_title)
    await message.answer("Введите название раздела:")


@router.message(AddSectionStates.waiting_for_title)
async def add_section_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AddSectionStates.waiting_for_description)
    await message.answer("Введите описание раздела (можно кратко):")


@router.message(AddSectionStates.waiting_for_description)
async def add_section_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(AddSectionStates.waiting_for_image_url)
    await message.answer(
        "Отправьте URL картинки для раздела (например, ссылка на картинку в интернете).\n"
        "Если картинки нет, напишите «-»."
    )


@router.message(AddSectionStates.waiting_for_image_url)
async def add_section_image(message: Message, state: FSMContext):
    image_url_raw = message.text.strip()
    image_url = None if image_url_raw == "-" else image_url_raw

    data = await state.get_data()
    section_id = await models.create_section(
        title=data["title"],
        description=data["description"],
        image_url=image_url,
    )

    await state.clear()
    await message.answer(f"Раздел создан! ID = {section_id}")


# ---------- /add_subsection ----------

@router.message(Command("add_subsection"))
async def cmd_add_subsection(message: Message, state: FSMContext):
    if not is_admin(message):
        await message.answer("Эта команда только для администратора.")
        return

    sections = await models.get_sections()
    if not sections:
        await message.answer("Сначала создайте хотя бы один раздел через /add_section.")
        return

    text_lines = ["Список разделов:"]
    for s in sections:
        text_lines.append(f"ID {s['id']}: {s['title']}")
    text_lines.append("\nВведите ID раздела, к которому относится подраздел:")

    await state.set_state(AddSubsectionStates.waiting_for_section_id)
    await message.answer("\n".join(text_lines))


@router.message(AddSubsectionStates.waiting_for_section_id)
async def add_subsection_section_id(message: Message, state: FSMContext):
    try:
        section_id = int(message.text.strip())
    except ValueError:
        await message.answer("Введите именно число — ID раздела.")
        return

    section = await models.get_section(section_id)
    if not section:
        await message.answer("Раздел с таким ID не найден. Попробуйте ещё раз.")
        return

    await state.update_data(section_id=section_id)
    await state.set_state(AddSubsectionStates.waiting_for_title)
    await message.answer("Введите название подраздела:")


@router.message(AddSubsectionStates.waiting_for_title)
async def add_subsection_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AddSubsectionStates.waiting_for_description)
    await message.answer("Введите описание подраздела:")


@router.message(AddSubsectionStates.waiting_for_description)
async def add_subsection_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(AddSubsectionStates.waiting_for_image_url)
    await message.answer(
        "Отправьте URL картинки для подраздела.\n"
        "Если не нужно, напишите «-»."
    )


@router.message(AddSubsectionStates.waiting_for_image_url)
async def add_subsection_image(message: Message, state: FSMContext):
    image_url_raw = message.text.strip()
    image_url = None if image_url_raw == "-" else image_url_raw

    data = await state.get_data()
    subsection_id = await models.create_subsection(
        section_id=data["section_id"],
        title=data["title"],
        description=data["description"],
        image_url=image_url,
    )

    await state.clear()
    await message.answer(f"Подраздел создан! ID = {subsection_id}")


# ---------- /add_material ----------

@router.message(Command("add_material"))
async def cmd_add_material(message: Message, state: FSMContext):
    if not is_admin(message):
        await message.answer("Эта команда только для администратора.")
        return

    sections = await models.get_sections()
    if not sections:
        await message.answer("Сначала создайте раздел через /add_section.")
        return

    text_lines = ["Список разделов:"]
    for s in sections:
        text_lines.append(f"ID {s['id']}: {s['title']}")
    text_lines.append("\nВведите ID раздела, к которому относится материал:")

    await state.set_state(AddMaterialStates.waiting_for_section_id)
    await message.answer("\n".join(text_lines))


@router.message(AddMaterialStates.waiting_for_section_id)
async def add_material_section_id(message: Message, state: FSMContext):
    try:
        section_id = int(message.text.strip())
    except ValueError:
        await message.answer("Введите именно число — ID раздела.")
        return

    section = await models.get_section(section_id)
    if not section:
        await message.answer("Раздел с таким ID не найден. Попробуйте ещё раз.")
        return

    subsections = await models.get_subsections_by_section(section_id)
    if not subsections:
        await message.answer("У этого раздела пока нет подразделов. Сначала создайте их через /add_subsection.")
        await state.clear()
        return

    await state.update_data(section_id=section_id)

    text_lines = [f"Подразделы раздела {section['title']}:"]
    for sb in subsections:
        text_lines.append(f"ID {sb['id']}: {sb['title']}")
    text_lines.append("\nВведите ID подраздела, к которому относится материал:")

    await state.set_state(AddMaterialStates.waiting_for_subsection_id)
    await message.answer("\n".join(text_lines))


@router.message(AddMaterialStates.waiting_for_subsection_id)
async def add_material_subsection_id(message: Message, state: FSMContext):
    try:
        subsection_id = int(message.text.strip())
    except ValueError:
        await message.answer("Введите именно число — ID подраздела.")
        return

    subsection = await models.get_subsection(subsection_id)
    if not subsection:
        await message.answer("Подраздел с таким ID не найден. Попробуйте ещё раз.")
        return

    await state.update_data(subsection_id=subsection_id)
    await state.set_state(AddMaterialStates.waiting_for_title)
    await message.answer("Введите название материала:")


@router.message(AddMaterialStates.waiting_for_title)
async def add_material_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AddMaterialStates.waiting_for_description)
    await message.answer("Введите описание материала (кратко):")


@router.message(AddMaterialStates.waiting_for_description)
async def add_material_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(AddMaterialStates.waiting_for_tg_link)
    await message.answer(
        "Отправьте ссылку на сообщение в Telegram (tg:// или https://t.me/... ).\n"
        "Если ссылки нет, напишите «-»."
    )


@router.message(AddMaterialStates.waiting_for_tg_link)
async def add_material_tg_link(message: Message, state: FSMContext):
    tg_link_raw = message.text.strip()
    tg_link = None if tg_link_raw == "-" else tg_link_raw

    await state.update_data(tg_link=tg_link)
    await state.set_state(AddMaterialStates.waiting_for_image_url)
    await message.answer(
        "Отправьте URL картинки для материала.\n"
        "Если не нужно, напишите «-»."
    )


@router.message(AddMaterialStates.waiting_for_image_url)
async def add_material_image(message: Message, state: FSMContext):
    image_url_raw = message.text.strip()
    image_url = None if image_url_raw == "-" else image_url_raw

    data = await state.get_data()
    material_id = await models.create_material(
        subsection_id=data["subsection_id"],
        title=data["title"],
        description=data["description"],
        tg_link=data["tg_link"],
        image_url=image_url,
    )

    await state.clear()
    await message.answer(f"Материал создан! ID = {material_id}")


# ---------- /edit ----------

@router.message(Command("edit"))
async def cmd_edit(message: Message, state: FSMContext):
    if not is_admin(message):
        await message.answer("Эта команда только для администратора.")
        return

    await state.set_state(EditStates.waiting_for_entity_type)
    await message.answer(
        "Что хотите изменить?\n"
        "1 — Раздел\n"
        "2 — Подраздел\n"
        "3 — Материал\n\n"
        "Отправьте цифру 1, 2 или 3."
    )


@router.message(EditStates.waiting_for_entity_type)
async def edit_choose_entity_type(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "1":
        entity_type = "section"
        entities = await models.get_sections()
        if not entities:
            await state.clear()
            await message.answer("Разделов пока нет.")
            return
        lines = ["Список разделов:"]
        for e in entities:
            lines.append(f"ID {e['id']}: {e['title']}")
        await message.answer("\n".join(lines))
    elif text == "2":
        entity_type = "subsection"
        # Покажем все подразделы
        # (для простоты, без группировки)
        from aiosqlite import connect
        from .config import get_settings

        db_path = get_settings().database_path
        async with connect(db_path) as db:
            db.row_factory = models._dict_factory
            await db.execute("PRAGMA foreign_keys = ON;")
            cursor = await db.execute(
                """
                SELECT sb.id, sb.title, sb.section_id, s.title AS section_title
                FROM subsections sb
                LEFT JOIN sections s ON s.id = sb.section_id
                ORDER BY sb.section_id ASC, sb.order_num ASC, sb.id ASC;
                """
            )
            rows = await cursor.fetchall()

        if not rows:
            await state.clear()
            await message.answer("Подразделов пока нет.")
            return

        lines = ["Список подразделов:"]
        for r in rows:
            lines.append(
                f"ID {r['id']}: {r['title']} (раздел {r['section_id']}: {r['section_title']})"
            )
        await message.answer("\n".join(lines))
    elif text == "3":
        entity_type = "material"
        # Покажем все материалы (упрощённо)
        from aiosqlite import connect
        from .config import get_settings

        db_path = get_settings().database_path
        async with connect(db_path) as db:
            db.row_factory = models._dict_factory
            await db.execute("PRAGMA foreign_keys = ON;")
            cursor = await db.execute(
                """
                SELECT m.id, m.title, m.subsection_id, sb.title AS subsection_title
                FROM materials m
                LEFT JOIN subsections sb ON sb.id = m.subsection_id
                ORDER BY m.subsection_id ASC, m.order_num ASC, m.id ASC;
                """
            )
            rows = await cursor.fetchall()

        if not rows:
            await state.clear()
            await message.answer("Материалов пока нет.")
            return

        lines = ["Список материалов:"]
        for r in rows:
            lines.append(
                f"ID {r['id']}: {r['title']} (подраздел {r['subsection_id']}: {r['subsection_title']})"
            )
        await message.answer("\n".join(lines))
    else:
        await message.answer("Введите только 1, 2 или 3.")
        return

    await state.update_data(entity_type=entity_type)
    await state.set_state(EditStates.waiting_for_entity_id)
    await message.answer("Отправьте ID записи, которую хотите изменить:")


@router.message(EditStates.waiting_for_entity_id)
async def edit_entity_id(message: Message, state: FSMContext):
    try:
        entity_id = int(message.text.strip())
    except ValueError:
        await message.answer("Введите число — ID.")
        return

    data = await state.get_data()
    entity_type = data["entity_type"]

    # Здесь мы не проверяем существование, просто пойдём дальше
    # (если ID неправильный, при сохранении будет тишина, но для новичка это проще).
    await state.update_data(entity_id=entity_id)
    await state.set_state(EditStates.waiting_for_field_name)

    if entity_type == "section":
        await message.answer(
            "Что изменить у раздела?\n"
            "Доступные поля: title, description, image_url, order_num\n"
            "Отправьте имя поля:"
        )
    elif entity_type == "subsection":
        await message.answer(
            "Что изменить у подраздела?\n"
            "Доступные поля: title, description, image_url, order_num, section_id\n"
            "Отправьте имя поля:"
        )
    else:
        await message.answer(
            "Что изменить у материала?\n"
            "Доступные поля: title, description, image_url, order_num, subsection_id, tg_link\n"
            "Отправьте имя поля:"
        )


@router.message(EditStates.waiting_for_field_name)
async def edit_field_name(message: Message, state: FSMContext):
    field_name = message.text.strip()
    data = await state.get_data()
    entity_type = data["entity_type"]

    valid_fields = {
        "section": {"title", "description", "image_url", "order_num"},
        "subsection": {"title", "description", "image_url", "order_num", "section_id"},
        "material": {
            "title",
            "description",
            "image_url",
            "order_num",
            "subsection_id",
            "tg_link",
        },
    }

    if field_name not in valid_fields[entity_type]:
        await message.answer("Неправильное имя поля. Попробуйте ещё раз.")
        return

    await state.update_data(field_name=field_name)
    await state.set_state(EditStates.waiting_for_new_value)
    await message.answer("Отправьте новое значение для этого поля:")


@router.message(EditStates.waiting_for_new_value)
async def edit_new_value(message: Message, state: FSMContext):
    new_value = message.text.strip()
    data = await state.get_data()
    entity_type = data["entity_type"]
    entity_id = data["entity_id"]
    field_name = data["field_name"]

    # Преобразуем к int для числовых полей
    int_fields = {"order_num", "section_id", "subsection_id"}
    if field_name in int_fields:
        try:
            new_value_casted = int(new_value)
        except ValueError:
            await message.answer("Это поле должно быть числом. Попробуйте ещё раз.")
            return
    else:
        new_value_casted = new_value

    if entity_type == "section":
        await models.update_section_field(entity_id, field_name, new_value_casted)
    elif entity_type == "subsection":
        await models.update_subsection_field(entity_id, field_name, new_value_casted)
    else:
        await models.update_material_field(entity_id, field_name, new_value_casted)

    await state.clear()
    await message.answer("Изменения сохранены.")