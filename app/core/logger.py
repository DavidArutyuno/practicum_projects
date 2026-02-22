import logging
import sys
from typing import Optional


_log_format = (
    '%(asctime)s - %(name)s - [%(levelname)s] - [%(color)s] - %(message)s - '
    '(%(filename)s -> %(funcName)s -> line %(lineno)d)'
)


class CustomFilter(logging.Filter):
    """Кастомное выделение сообщений в журналировании."""

    COLORS = {
        'DEBUG': 'GREEN',
        'INFO': 'GREEN',
        'WARNING': 'YELLOW',
        'ERROR': 'RED',
        'CRITICAL': 'RED',
    }

    def filter(self, record):
        """Добавляем свой фильтр."""
        record.color = self.COLORS.get(record.levelname, 'WHITE')
        return True


def get_console_handler():
    """Создаем обработчик для вывода логов в консоль."""
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(_log_format))
    return console_handler


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Создание журналирования.

    Args:
        name: Имя логгера (обычно __name__)
        level: Уровень логирования (по умолчанию INFO)

    Returns:
        Настроенный логгер
    """
    logger = logging.getLogger(name)

    if level:
        logger.setLevel(level)
    else:
        logger.setLevel(logging.INFO)

    # Добавляем фильтр, если его ещё нет
    if not any(isinstance(f, CustomFilter) for f in logger.filters):
        logger.addFilter(CustomFilter())

    # Добавляем обработчик, если его ещё нет
    if not logger.handlers:
        logger.addHandler(get_console_handler())

    return logger


# Создаём основной логгер приложения
logger = get_logger(__name__)