"""My Bot Assistant with extended functionality."""
from datetime import datetime
import logging
import os
import requests
import sqlite3
import sys
import time
from contextlib import closing

from dotenv import load_dotenv
from http import HTTPStatus
from telebot import TeleBot, types
import exceptions

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
    '(%(filename)s -> %(funcName)s -> line %(lineno)d)'
)


class BotState:
    """Class to store bot state."""
    last_api_check = None
    last_error = None


class CustomFilter(logging.Filter):
    """Custom logging filter for colored output."""
    COLOR = {
        "DEBUG": "GREEN",
        "INFO": "GREEN",
        "WARNING": "YELLOW",
        "ERROR": "RED",
        "CRITICAL": "RED",
    }

    def filter(self, record):
        """Add color to log records."""
        record.color = CustomFilter.COLOR[record.levelname]
        return True


def get_stream_handler():
    """Create stream handler for logging."""
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def get_logger(name):
    """Create and configure logger."""
    logger = logging.getLogger(name)
    logger.addFilter(CustomFilter())
    logger.addHandler(get_stream_handler())
    return logger


logger = get_logger(__name__)


def init_db():
    """Initialize DB with technical and human-readable status fields."""
    with closing(sqlite3.connect('bot_history.db')) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS status_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                homework_name TEXT NOT NULL,
                status_code TEXT NOT NULL,  -- Технический статус (approved/reviewing/rejected)
                status_text TEXT NOT NULL   -- Человекочитаемый статус (текст из HOMEWORK_VERDICTS)
            )
        ''')
        conn.commit()


def save_status_to_db(homework_name, status_code, status_text):
    """Save both technical and human-readable statuses."""
    with closing(sqlite3.connect('bot_history.db')) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO status_history (homework_name, status_code, status_text)
            VALUES (?, ?, ?)
        ''', (homework_name, status_code, status_text))
        conn.commit()


def check_tokens():
    """Check required environment variables."""
    environments_variables = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    for key, value in environments_variables.items():
        if value is None or value == '':
            raise exceptions.EnvironmentError(
                logger.critical(
                    f'Отсутствует обязательная переменная окружения: {key}'
                    '\n Программа принудительно остановлена.'
                )
            )
    logger.debug('Функция check_tokens выполнена.')
    return True


def send_message(bot: TeleBot, message):
    """Send message to Telegram chat."""
    try:
        chat_id = TELEGRAM_CHAT_ID
        bot.send_message(
            chat_id=chat_id,
            text=message,
        )
    except exceptions.ApiTelegramException as error:
        raise exceptions.ApiTelegramException(error)
    else:
        logger.debug(f'Сообщение отправлено: {message}')


def get_api_answer(timestamp):
    """Get API response."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=payload
        )
        if response.status_code != HTTPStatus.OK:
            raise exceptions.ResponseStatusCodeError(
                f'API вернул код {response.status_code}, отличный от 200.'
            )
    except requests.exceptions as error:
        raise Exception.ApiRequestException(error)
    else:
        logger.debug('Функция get_api_answer выполнена.')
    try:
        return response.json()
    except exceptions.JSONDecodeError as error:
        raise exceptions.JSONDecodeError(error)


def check_response(response):
    """Check API response structure."""
    if not isinstance(response, dict):
        raise exceptions.TypeResponseIsNotDictError(
            'В ответе API не найден словарь с данными.'
        )

    if 'homeworks' not in response:
        raise exceptions.HomeworksNotInResponseError(
            'В ответе API в словаре нет ключа "homeworks".'
        )

    if not isinstance(response['homeworks'], list):
        raise exceptions.TypeHomeworksIsNotListError(
            'В ответе API под ключом "homeworks" не найден список.'
        )

    if len((response['homeworks'])) == 0:
        logger.debug('Получен пустой список домашних работ.')
        raise exceptions.ValueHomeworksError(
            'Получен пустой список домашних работ.'
        )
    logger.debug('Функция check_response выполнена.')
    return True


def parse_status(homework):
    """Extract and save both status versions."""
    for key in KEY_DICT_HOMEWORKS:
        if key not in homework:
            raise exceptions.UnknownStatusHomeworksError(
                f'Отсутствует ключ "{key}".'
            )

    homework_name = homework['homework_name']

    # Технический статус (approved/reviewing/rejected)
    status_code = homework['status']
    status_text = HOMEWORK_VERDICTS[status_code]  # Читаемый текст

    save_status_to_db(homework_name, status_code, status_text)

    return f'Изменился статус работы "{homework_name}". {status_text}'


def format_history(records):
    """Format history records for display."""
    return "\n".join(
        f"⏰ {r[0]}\n📝 {r[1]}\n🔄 {r[2]}\n——————————"
        for r in records
    )


def main():
    """Main bot logic."""

    init_db()  # Initialize database

    if check_tokens():
        bot = TeleBot(token=TELEGRAM_TOKEN)
        timestamp = int(time.time() - FOR_MONTH)
        update_homework = dict()
        last_error_message = ''

        @bot.message_handler(commands=['status'])
        def send_bot_status(message):
            """Send bot status with interactive keyboard."""
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(types.KeyboardButton('Проверить сейчас 🔄'))
            keyboard.add(types.KeyboardButton('История статусов 📜'))

            bot.send_message(
                message.chat.id,
                "🤖 Выберите действие:",
                reply_markup=keyboard,
            )

        @bot.message_handler(func=lambda msg: msg.text == 'Проверить сейчас 🔄')
        def force_check_status(message):
            """Force immediate API check."""
            try:
                response = get_api_answer(int(time.time() - FOR_MONTH))
                if check_response(response):
                    homework = response['homeworks'][0]
                    status_msg = parse_status(homework)
                    bot.send_message(
                        message.chat.id, f"🔍 Результат:\n{status_msg}")
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

        @bot.message_handler(func=lambda msg: msg.text == 'История статусов 📜')
        def show_history(message):
            with closing(sqlite3.connect('bot_history.db')) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT timestamp, homework_name, status_text 
                    FROM status_history 
                    ORDER BY timestamp DESC 
                    LIMIT 5
                ''')
                history = cursor.fetchall()

            # Выводим читаемый статус (status_text)
            bot.send_message(message.chat.id, format_history(history))

            if not history:
                bot.send_message(message.chat.id, "История пуста.")
                return

            history_text = "📜 Последние 5 статусов:\n\n"
            for record in history:
                time, name, status = record
                history_text += (
                    f"⏰ *{time}*\n"
                    f"📌 *{name}* → `{status}`\n"
                    f"————————————\n"
                )

            bot.send_message(
                message.chat.id,
                history_text,
                parse_mode="Markdown"
            )

        # Start polling in background
        bot.polling(non_stop=True, interval=0)

        while True:
            try:
                logger.debug('Запрос к API Яндекс.Практикума.')
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
                        BotState.last_api_check = datetime.now()
                        BotState.last_error = None
            except BaseException as error:
                message = f'Сбой в работе программы: {error}'
                logger.error(message, exc_info=True)
                BotState.last_error = message
                if message != last_error_message:
                    send_message(bot, message)
                    last_error_message = message
            finally:
                time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
