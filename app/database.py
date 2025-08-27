from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from .logging_config import log

# Загрузка переменных окружения
load_dotenv()

# Получение параметров подключения из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clothing_store.db")

# Создание движка базы данных
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Функция для получения сессии базы данных
def get_db():
    """
    Генератор сессий базы данных.
    Обеспечивает корректное закрытие сессии после использования.
    """
    db = SessionLocal()
    try:
        log.info("Создана новая сессия базы данных")
        yield db
    finally:
        db.close()
        log.info("Сессия базы данных закрыта")

# Функция для создания таблиц
def create_tables():
    """Создание всех таблиц в базе данных"""
    try:
        Base.metadata.create_all(bind=engine)
        log.info("Таблицы базы данных успешно созданы")
    except Exception as e:
        log.error(f"Ошибка при создании таблиц: {e}")
        raise