import logging
from loguru import logger
import sys


# Настройка логирования
def setup_logging():
    """Настройка системы логирования для приложения"""

    # Удаляем стандартный обработчик loguru
    logger.remove()

    # Добавляем обработчик для вывода в консоль
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )

    # Добавляем обработчик для записи в файл
    logger.add(
        "logs/app.log",
        rotation="10 MB",  # Ротация при достижении 10MB
        retention="30 days",  # Хранение логов 30 дней
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )

    # Перехватываем стандартное логирование Python
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Получаем соответствующий уровень loguru
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Находим фрейм, откуда пришел вызов
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    # Настраиваем стандартное логирование
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    return logger


# Инициализация логгера
log = setup_logging()