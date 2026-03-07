import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from aiohttp import web

from .config import get_settings
from .database import init_db
from .handlers import router as bot_router
from . import models

# Включаем простой логгинг в консоль
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------- AIOHTTP API (для Mini App) ----------

async def handle_get_sections(request: web.Request) -> web.Response:
    """
    GET /api/sections
    Вернуть список всех разделов (JSON).
    """
    sections = await models.get_sections()
    return web.json_response({"sections": sections})


async def handle_get_section_subsections(request: web.Request) -> web.Response:
    """
    GET /api/sections/{id}/subsections
    Вернуть подразделы конкретного раздела.
    """
    section_id = int(request.match_info["id"])
    subsections = await models.get_subsections_by_section(section_id)
    # Дополнительно вернём информацию о самом разделе
    section = await models.get_section(section_id)
    return web.json_response(
        {
            "section": section,
            "subsections": subsections,
        }
    )


async def handle_get_subsection_materials(request: web.Request) -> web.Response:
    """
    GET /api/subsections/{id}/materials
    Вернуть материалы конкретного подраздела.
    """
    subsection_id = int(request.match_info["id"])
    materials = await models.get_materials_by_subsection(subsection_id)
    subsection = await models.get_subsection(subsection_id)
    return web.json_response(
        {
            "subsection": subsection,
            "materials": materials,
        }
    )


def create_web_app() -> web.Application:
    """
    Создаём и настраиваем aiohttp-приложение.
    Здесь будут только API-эндпоинты /api/...
    Статические файлы (HTML/JS/CSS) будет отдавать nginx.
    """
    app = web.Application()
    app.router.add_get("/api/sections", handle_get_sections)
    app.router.add_get("/api/sections/{id}/subsections", handle_get_section_subsections)
    app.router.add_get(
        "/api/subsections/{id}/materials",
        handle_get_subsection_materials,
    )
    return app


# ---------- ЗАПУСК БОТА И ВЕБ-СЕРВЕРА ----------

async def main():
    settings = get_settings()
    await init_db()

    bot = Bot(token=settings.bot_token, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(bot_router)

    # Создаём aiohttp-приложение и запускаем его
    web_app = create_web_app()
    runner = web.AppRunner(web_app)
    await runner.setup()
    # Слушаем на 0.0.0.0:8000
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()
    logger.info("HTTP API запущено на http://0.0.0.0:8000")

    # Запускаем бота (long polling) в этом же процессе
    try:
        logger.info("Бот запускается (long polling)...")
        await dp.start_polling(bot)
    finally:
        logger.info("Остановка бота и HTTP-сервера...")
        await runner.cleanup()
        await bot.session.close()


if __name__ == "__main__":
    # Для Windows в разработке иногда нужен этот фикс,
    # но на Debian обычно не требуется.
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())