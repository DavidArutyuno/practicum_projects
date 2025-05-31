"""My Bot Assistant."""

import json
import logging
import os
import requests
import sys
import time

from dotenv import load_dotenv
from http import HTTPStatus
from telebot import TeleBot

import Exception

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

FOR_MONTH = 2629743
RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

KEY_DICT_HOMEWORKS = [
    'date_updated',
    'homework_name',
    'id',
    'lesson_name',
    'reviewer_comment',
    'status'
]

_log_format = (
    '%(asctime)s - %(name)s - [%(levelname)s] - [%(color)s] - %(message)s - '
    + '(%(filename)s -> %(funcName)s -> line %(lineno)d)'
)


class CustomFilter(logging.Filter):
    """Кастомное выделение сообщений в журналировании."""

    COLOR = {
        "DEBUG": "GREEN",
        "INFO": "GREEN",
        "WARNING": "YELLOW",
        "ERROR": "RED",
        "CRITICAL": "RED",
    }

    def filter(self, record):
        """Добавляем свой фильтр."""
        record.color = CustomFilter.COLOR[record.levelname]
        return True


def get_stream_handler():
    """Создаем обработчик для вывода логов в терминал."""
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def get_logger(name):
    """Создание журналирования."""
    logger = logging.getLogger(name)
    logger.addFilter(CustomFilter())
    logger.addHandler(get_stream_handler())
    return logger


logger = get_logger(__name__)


def check_tokens():
    """
    Проверка доступности переменных окружения.

    Если отсутствует хотя бы одна переменная окружения — выполнение программы
    остановится, а событие запишется в журнал (лог).
    """
    environments_variables = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    for key, value in environments_variables.items():
        if (value is None) or (value == ''):
            raise Exception.EnvironmentError(
                logger.critical(
                    f'Отсутствует обязательная переменная окружения: {key}'
                    '\n Программа принудительно остановлена.'
                )
            )
    logger.debug('Функция check_tokens выполнена.')
    return True


def send_message(bot: TeleBot, message):
    """
    Отправка сообщений.

    Функция отправляет сообщение в Telegram-чат, определяемый переменной
    окружения TELEGRAM_CHAT_ID.
    Принимает на вход два параметра:
        экземпляр класса TeleBot и
        строку с текстом сообщения.
    """
    try:
        chat_id = TELEGRAM_CHAT_ID
        bot.send_message(
            chat_id=chat_id,
            text=message,
        )
    except Exception.ApiTelegramException as error:
        return f'При отправки сообщения в Telegram произошла ошибка: {error}'
    else:
        logger.debug(f'Сообщение отправлено: {message}')


def get_api_answer(timestamp):
    """
    Получение ответа от API (Практикум Домашка).

    Делает запрос к единственному эндпоинту API-сервиса.
    В качестве параметра в функцию передаётся временная метка.
    В случае успешного запроса возвращается ответ API
    приведенный из формата JSON к типам данных Python.
    """
    payload = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=payload
        )
        if response.status_code != HTTPStatus.OK:
            raise Exception.ResponseStatusCodeError(
                f'API (Практикум Домашка) вернул код {response.status_code}, '
                + 'отличный от 200.'
            )
    except requests.exceptions.HTTPError as error:
        return f'Произошла ошибка HTTP: {error}'
    except requests.exceptions.RequestException as error:
        return f'При обработке запроса произошло исключение: {error}'
    else:
        logger.debug('Функция get_api_answer выполнена.')
    try:
        return response.json()
    except json.decoder.JSONDecodeError:
        null_response = {
            'current_date': time.time(),
            'homeworks': []
        }
        return null_response


def check_response(response):
    """
    Проверка ответа от API.

    Проверяет ответ API на соответствие документации
    из урока «API сервиса Практикум Домашка».
    В качестве параметра функция получает ответ API,
    приведённый к типам данных Python.
    """
    if not isinstance(response, dict):
        raise Exception.TypeResponseIsNotDictError(
            'В ответе API не найден словарь с данными.'
        )

    if 'homeworks' not in response:
        raise Exception.HomeworksNotInResponseError(
            'В ответе API в словаре нет ключа "homeworks".'
        )

    if not isinstance(response['homeworks'], list):
        raise Exception.TypeHomeworksIsNotListError(
            'В ответе API под ключом "homeworks" не найден список.'
        )

    if len((response['homeworks'])) == 0:
        logger.debug('Получен пустой список домашних работ.')
        raise Exception.ValueHomeworksError(
            'Получен пустой список домашних работ.'
        )
    logger.debug('Функция check_response выполнена.')
    return True


def parse_status(homework):
    """
    Проверка статуса работы.

    Функция parse_status() извлекает из информации о конкретной домашней работе
    статус этой работы. В качестве параметра функция получает только
    один элемент из списка домашних работ. В случае успеха функция возвращает
    подготовленную для отправки в Telegram строку, содержащую один из вердиктов
    словаря HOMEWORK_VERDICTS.
    """
    for key in KEY_DICT_HOMEWORKS:
        if key not in homework:
            raise Exception.UnknownStatusHomeworksError(
                f'В ответе API, в словаре отсутствует ключ "{key}".'
            )

    for key, value in HOMEWORK_VERDICTS.items():
        if homework['status'] == key:
            homework_name = homework['homework_name']
            verdict = value
    logger.debug('Функция parse_status выполнена.')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if check_tokens():
        bot = TeleBot(token=TELEGRAM_TOKEN)
        timestamp = int(time.time() - FOR_MONTH)
        update_homework = dict()
        last_error_message = ''

        while True:
            try:
                logger.debug('Запрос к «API сервису Практикум Домашка».')
                response_dict = get_api_answer(timestamp=timestamp)

                if (check_response(response_dict)
                        and (response_dict['homeworks'] != [])):
                    last_homework = response_dict['homeworks'][0]
                    if last_homework != update_homework:
                        new_status = parse_status(
                            response_dict['homeworks'][0]
                        )
                        logger.info('Обновился статус домашки.')
                        send_message(bot=bot, message=new_status)
                        update_homework = last_homework
            except BaseException as error:
                message = f'Сбой в работе программы: {error}'
                logger.error(message, exc_info=True)
                if message != last_error_message:
                    send_message(bot, message)
                    last_error_message = message
            finally:
                time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
