"""Иключения для работы бот ассистента."""

import json

from requests.exceptions import (
    HTTPError, ConnectionError, Timeout, RequestException
)
from telebot.apihelper import ApiException


class EnvironmentError(ConnectionError):
    """Ошибки переменных окружения."""


class ResponseStatusCodeError(Exception):
    """Ошибки статусов ответов от API (Практикум Домашка)."""


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


class ApiTelegramException(ApiException, RequestException):
    """Ошибка при обращении к API telegramm."""


class ApiRequestException(HTTPError, RequestException):
    """Ошибка при обращении к API сервису Практикум Домашка."""


class JSONDecodeError(json.decoder.JSONDecodeError):
    """Ошибка при декодировании строки JSON."""
