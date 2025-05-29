import logging
import os
import requests
import sys
import time

from dotenv import load_dotenv
from http import HTTPStatus
from telebot import TeleBot

import Exception as e

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

OFFSET = 3600000
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
    f'%(asctime)s - ' +
    f'%(name)s - ' +
    f'[%(levelname)s] - ' +
    f'[%(color)s] - ' +
    f'%(message)s - ' +
    f'(%(filename)s).%(funcName)s(%(lineno)d)'
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

    Если отсутствует хотя бы одна переменная окружения — функция вернет False и
    выполнение программы остановится, а событие запишется в журнал (лог).
    """
    environments_variables = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    for key, value in environments_variables.items():
        if value is None:
            logger.critical(
                f'Отсутствует обязательная переменная окружения: {key}'
                '\n Программа принудительно остановлена.'
            )
            raise EnvironmentError(
                f'Отсутствует обязательная переменная окружения: {key}'
                '\n Программа принудительно остановлена.'
            )
    return True


def send_message(bot: TeleBot, message: str):
    """
    Отправка сообщений.

    Функция отправляет сообщение в Telegram-чат, определяемый переменной
    окружения TELEGRAM_CHAT_ID.
    Принимает на вход два параметра:
        экземпляр класса TeleBot и
        строку с текстом сообщения.
    """
    chat_id = TELEGRAM_CHAT_ID

    bot.send_message(
        chat_id=chat_id,
        text=message,
    )

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
            logger.error(
                f'{response.json()['code']}: ' +
                'API домашки возвращает код, отличный от 200.'
            )
            raise e.ResponseStatusCodeError(
                'API домашки возвращает код, отличный от 200.'
            )
    except requests.exceptions.HTTPError as error:
        logger.error(f'Произошла ошибка HTTP: {error}')
    except requests.exceptions.RequestException as error:
        logger.error(
            'При обработке запроса произошло ' +
            f'неоднозначное исключение: {error}'
        )
    return response.json()


def check_response(response: requests):
    """
    Проверка ответа от API.

    Проверяет ответ API на соответствие документации
    из урока «API сервиса Практикум Домашка».
    В качестве параметра функция получает ответ API,
    приведённый к типам данных Python.
    """
    if type(response) != dict:
        logger.error('В ответе API не найден словарь с данными.')
        raise e.TypeResponseIsNotDictError(
            'В ответе API не найден словарь с данными.'
        )

    if 'homeworks' not in response:
        logger.error('В ответе API в словаре нет ключа "homeworks".')
        raise e.HomeworksNotInResponseError(
            'В ответе API в словаре нет ключа "homeworks".'
        )

    if type(response['homeworks']) != list:
        logger.error(
            'В ответе API под ключом "homeworks" значение '
            'не является списоком.'
        )
        raise e.TypeHomeworksIsNotListError(
            'В ответе API под ключом "homeworks" значение '
            'не является списоком.'
        )

    if len((response['homeworks'])) == 0:
        logger.debug('Получен пустой список домашних работ.')
        raise e.ValueHomeworksError(
            'Получен пустой список домашних работ.'
        )

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
        if key not in homework.keys():
            logger.error(
                'В ответе API, в словаре данных ' +
                f'отсутствует ожидаемый ключ "{key}".'
            )
            raise e.UnknownStatusHomeworksError(
                'В ответе API, в словаре данных ' +
                f'отсутствует ожидаемый ключ "{key}".'
            )

    # if homework['status'] not in HOMEWORK_VERDICTS.keys():
    #     logger.error(
    #         f'Неожиданный статус домашней работы: {homework['status']}'
    #     )
    #     raise e.UnknownStatusHomeworksError(
    #         'Неожиданный статус домашней работы, обнаруженный в ответе API'
    #     )

    for key, value in HOMEWORK_VERDICTS.items():
        if homework['status'] == key:
            homework_name = homework['homework_name']
            verdict = value

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if check_tokens():
        bot = TeleBot(token=TELEGRAM_TOKEN)
        timestamp = int(time.time() - OFFSET)

        while True:
            try:

                response_dict = get_api_answer(timestamp=timestamp)
                if check_response(response_dict):
                    send_message(
                        bot=bot,
                        message=parse_status(response_dict['homeworks'][0])
                    )
            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                logger.error(message)
            finally:
                time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
