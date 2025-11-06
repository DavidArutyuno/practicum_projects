# main.py
import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

# Добавьте к списку импортов импорт функции с конфигурацией
# парсера аргументов командной строки и функцию configure_logging()
from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, PEP_DOC_URL
from outputs import control_output
from utils import find_tag, get_response, parse_pep_field_list


def whats_new(session):
    # Вместо константы WHATS_NEW_URL, используйте переменную whats_new_url.
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')

    # Замените код загрузки страницы и установки кодировки
    # на вызов функции get_response().
    # response = session.get(whats_new_url)
    # response.encoding = 'utf-8'
    response = get_response(session, whats_new_url)
    if response is None:
        # Если основная страница не загрузится, программа закончит работу.
        return

    # Создание "супа".
    soup = BeautifulSoup(response.text, features='lxml')

    # Шаг 1-й: поиск в "супе" тега section с нужным id. Парсеру нужен только
    # первый элемент, поэтому используется метод find().
    # main_div = soup.find('section', attrs={'id': 'what-s-new-in-python'})
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})

    # Шаг 2-й: поиск внутри main_div следующего тега div с классом toctree-wrapper.
    # Здесь тоже нужен только первый элемент, используется метод find().
    # div_with_ul = main_div.find('div', attrs={'class': 'toctree-wrapper'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})

    # Шаг 3-й: поиск внутри div_with_ul всех элементов списка li с классом toctree-l1.
    # Нужны все теги, поэтому используется метод find_all().
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'})

    # Печать первого найденного элемента.
    # print(sections_by_python[0].prettify())

    # Добавьте в пустой список заголовки таблицы.
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python, desc='Парсинг'):
        version_a_tag = section.find('a')
        # version_a_tag = section.find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)

        # Загрузите все страницы со статьями. Используйте кеширующую сессию.
        # Замените код загрузки страницы и установки кодировки
        # на вызов функции get_response().
        # response = session.get(version_link)
        # response.encoding = 'utf-8'
        response = get_response(session, version_link)
        if response is None:
            # Если страница не загрузится, программа перейдёт к следующей ссылке.
            continue

        # Сварите "супчик".
        soup = BeautifulSoup(response.text, features='lxml')
        # h1 = soup.find('h1')  # Найдите в "супе" тег h1.
        h1 = find_tag(soup, 'h1')
        # dl = soup.find('dl')  # Найдите в "супе" тег dl.
        dl = find_tag(soup, 'dl')  # Найдите в "супе" тег dl.

        # На печать теперь выводится переменная dl_text — без пустых строчек.
        dl_text = dl.text.replace('\n', ' ')
        # print(version_link, h1.text, dl_text)

        # Добавьте в список ссылки и текст из тегов h1 и dl в виде кортежа.
        results.append(
            (version_link, h1.text, dl_text)
        )

    # print('\n')
    # # Печать списка с данными.
    # for row in results:
    #     # Распаковка каждого кортежа при печати при помощи звездочки.
    #     print(*row)

    # Вместо вывода списка на печать верните этот список.
    return results


def latest_versions(session):
    # session = requests_cache.CachedSession()
    # Замените код загрузки страницы и установки кодировки
    # на вызов функции get_response().
    # response = session.get(MAIN_DOC_URL)
    # response.encoding = 'utf-8'
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')
    # sidebar = soup.find('div', {'class': 'sphinxsidebarwrapper'})
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    # Перебор в цикле всех найденных списков.
    for ul in ul_tags:
        # Проверка, есть ли искомый текст в содержимом тега.
        if 'All versions' in ul.text:
            # Если текст найден, ищутся все теги <a> в этом списке.
            a_tags = ul.find_all('a')
            # Остановка перебора списков.
            break
    # Если нужный список не нашёлся,
    # вызывается исключение и выполнение программы прерывается.
    else:
        raise Exception('Ничего не нашлось')

    # Добавьте в пустой список заголовки таблицы.
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    # Цикл для перебора тегов <a>, полученных ранее.
    for a_tag in a_tags:
        # Извлечение ссылки.
        link = a_tag['href']
        # Поиск паттерна в ссылке.
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            # Если строка соответствует паттерну,
            # переменным присываивается содержимое групп, начиная с первой.
            version, status = text_match.groups()
        else:
            # Если строка не соответствует паттерну,
            # первой переменной присваивается весь текст, второй — пустая строка.
            version, status = a_tag.text, ''
        # Добавление полученных переменных в список в виде кортежа.
        results.append(
            (link, version, status)
        )

    # print('\n')
    # Вместо вывода списка на печать верните этот список.
    # for row in results:
        # print(*row)
    return results


def download(session):
    # Вместо константы DOWNLOADS_URL, используйте переменную downloads_url.
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    # session = requests_cache.CachedSession()
    # Замените код загрузки страницы и установки кодировки
    # на вызов функции get_response().
    # response = session.get(downloads_url)
    # response.encoding = 'utf-8'
    response = get_response(session, downloads_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')
    # table_tag = soup.find('table', {'class': 'docutils'})
    table_tag = find_tag(soup, 'table', {'class': 'docutils'})
    # Добавьте команду получения нужного тега.
    # epub_tag = find_tag(table_tag, 'a', {'href': re.compile(r'.+docs\.epub$')})
    epub_tag = find_tag(table_tag, 'a', {'href': re.compile(r'.+html\.zip$')})
    # Сохраните в переменную содержимое атрибута href.
    epub_link = epub_tag['href']
    # Получите полную ссылку с помощью функции urljoin.
    archive_url = urljoin(downloads_url, epub_link)
    filename = archive_url.split('/')[-1]
    # Сформируйте путь до директории downloads.
    downloads_dir = BASE_DIR / 'downloads'
    print(BASE_DIR)
    print(downloads_dir)
    # Создайте директорию.
    downloads_dir.mkdir(exist_ok=True)
    # Получите путь до архива, объединив имя файла с директорией.
    archive_path = downloads_dir / filename

    # Загрузка архива по ссылке.
    response = session.get(archive_url)

    # В бинарном режиме открывается файл на запись по указанному пути.
    with open(archive_path, 'wb') as file:
        # Полученный ответ записывается в файл.
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, PEP_DOC_URL)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')

    table_tags = soup.find_all(
        'table', attrs={'class': 'pep-zero-table docutils align-default'})

    details_pep = []
    for table_tag in tqdm(table_tags, 'Парсинг: '):
        td_tags = table_tag.find_all('td')
        id = 0
        for td_tag in td_tags:

            # Статус из общей таблицы PEP
            first_column_tag = td_tag.find('abbr')
            if first_column_tag:
                preview_status = first_column_tag.text[1:]
                id = id + 1

            a_tag = td_tag.find(
                'a', attrs={'class': 'pep reference internal'})

            # Парсим детальный PEP по ссылкам
            if a_tag and a_tag.text.strip().isdigit():
                href = a_tag['href']
                pep_link = urljoin(PEP_DOC_URL, href)

                response = session.get(pep_link)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, features='lxml')
                dl = soup.find(
                    'dl', attrs={'class': 'rfc2822 field-list simple'})
                details_pep.append(
                    parse_pep_field_list(dl, preview_status, pep_link)
                )

    statistics_status = {
        'Active': 0,
        'Accepted': 0,
        'Deferred': 0,
        'Final': 0,
        'Provisional': 0,
        'Rejected': 0,
        'Superseded': 0,
        'Withdrawn': 0,
        'Draft': 0,
        'Active': 0,
        'April Fool!': 0,
        'Total': 0,
    }
    for detail in details_pep:
        statistics_status[detail['Status']] += 1
        statistics_status['Total'] += 1

    results = [('Статус', 'Количество')]
    for key, value in statistics_status.items():
        print(key, value)
        results.append((key, str(value)))

    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    print(BASE_DIR)
    # Запускаем функцию с конфигурацией логов.
    configure_logging()
    # Отмечаем в логах момент запуска программы.
    logging.info('Парсер запущен!')

    # Конфигурация парсера аргументов командной строки —
    # передача в функцию допустимых вариантов выбора.
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    # Считывание аргументов из командной строки.
    args = arg_parser.parse_args()

    # Логируем переданные аргументы командной строки.
    logging.info(f'Аргументы командной строки: {args}')

    # Создание кеширующей сессии.
    session = requests_cache.CachedSession()
    # Если был передан ключ '--clear-cache', то args.clear_cache == True.
    if args.clear_cache:
        # Очистка кеша.
        session.cache.clear()

    # Получение из аргументов командной строки нужного режима работы.
    parser_mode = args.mode
    # Поиск и вызов нужной функции по ключу словаря.
    # С вызовом функции передаётся и сессия.
    # MODE_TO_FUNCTION[parser_mode](session)

    # Сохраняем результат вызова функции в переменную results.
    results = MODE_TO_FUNCTION[parser_mode](session)

    # Если из функции вернулись какие-то результаты,
    if results is not None:
        # передаём их в функцию вывода вместе с аргументами командной строки.
        control_output(results, args)

    # Логируем завершение работы парсера.
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
