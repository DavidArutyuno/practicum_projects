class EnvironmentError(ConnectionError):
    """Ошибки окружения."""
    pass


class ResponseStatusCodeError(Exception):
    """Ошибки статусов ответов."""
    pass


class TypeResponseIsNotDictError(TypeError):
    """Ошибки окружения."""
    pass


class HomeworksNotInResponseError(KeyError):
    """Отсутствие ключа в словаре."""
    pass


class TypeHomeworksIsNotListError(TypeError):
    """Не верный тип данных в ответе."""
    pass


class UnknownStatusHomeworksError(KeyError):
    """Отсутствие ключа в словаре."""
    pass


class ValueHomeworksError(ValueError):
    """Получен пустой список домашних работ."""
    pass
