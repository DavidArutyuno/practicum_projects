"""Иключения для работы бот ассистента."""

from requests.exceptions import HTTPError, ConnectionError, Timeout


class EnvironmentError(ConnectionError):
    """Ошибки окружения."""


class ResponseStatusCodeError(Exception):
    """Ошибки статусов ответов."""


class TypeResponseIsNotDictError(TypeError):
    """Ответ не содержит словарь данных."""


class HomeworksNotInResponseError(KeyError):
    """Отсутствие ключа в словаре."""


class TypeHomeworksIsNotListError(TypeError):
    """Не верный тип данных в ответе."""


class UnknownStatusHomeworksError(KeyError):
    """Отсутствие ключа в словаре."""


class ValueHomeworksError(ValueError):
    """Получен пустой список домашних работ."""


class ApiTelegramException(ConnectionError, HTTPError, Timeout):
    """Ошибка при обращении к API telegramm."""
