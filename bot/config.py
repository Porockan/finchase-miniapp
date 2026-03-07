import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
# Файл .env должен лежать в корне проекта (finchase-miniapp/.env)
load_dotenv()


@dataclass
class Settings:
    bot_token: str
    admin_chat_id: int
    webapp_url: str
    database_path: str


def get_settings() -> Settings:
    """
    Прочитать настройки из переменных окружения.
    Если чего-то не хватает, выбросим понятную ошибку.
    """
    bot_token = os.getenv("BOT_TOKEN")
    admin_chat_id = os.getenv("ADMIN_CHAT_ID")
    webapp_url = os.getenv("WEBAPP_URL")
    database_path = os.getenv("DATABASE_PATH", "database.db")

    if not bot_token:
        raise ValueError("Не задан BOT_TOKEN в .env")
    if not admin_chat_id:
        raise ValueError("Не задан ADMIN_CHAT_ID в .env")
    if not webapp_url:
        raise ValueError("Не задан WEBAPP_URL в .env")

    return Settings(
        bot_token=bot_token,
        admin_chat_id=int(admin_chat_id),
        webapp_url=webapp_url,
        database_path=database_path,
    )