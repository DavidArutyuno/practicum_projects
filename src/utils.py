import logging

from requests import RequestException
from exceptions import ParserFindTagException

from constants import EXPECTED_STATUS


def get_response(session, url):
    """Перехват ошибки RequestException."""
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def find_tag(soup, tag, attrs=None):
    """Перехват ошибки поиска тегов."""
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def parse_pep_field_list(soup, pre_status, link):
    """Парсит всю field-list таблицу PEP."""
    field_list = {}

    dt_tags = soup.select('dl.field-list dt')

    for dt_tag in dt_tags:
        field_name = dt_tag.text.strip()
        field_name = str.replace(field_name, ':', '')
        dd_tag = dt_tag.find_next_sibling('dd')
        field_value = dd_tag.text.strip() if dd_tag else None
        field_list[field_name] = field_value
        if field_name == 'Status':
            if field_value not in EXPECTED_STATUS[pre_status]:
                error_msg = (
                    f'Несовпадающие статусы: \n'
                    f'{link}\n'
                    f'Статус в карточке: {field_value}\n'
                    f'Ожидаемые статусы: {EXPECTED_STATUS[pre_status]}\n'
                )
                logging.info(error_msg)
    return field_list
