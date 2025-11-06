import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, PEP_DOC_URL
from exceptions import ParserFindTagException
from outputs import control_output
from utils import find_tag, get_response, get_soup, parse_pep_field_list


def whats_new(session):
    soup, whats_new_url = get_soup(
        session=session,
        doc_url=MAIN_DOC_URL,
        tail_url='whatsnew/'
    )

    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'})
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python, desc='Парсинг'):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)

        response = get_response(session, version_link)
        if response is None:
            continue

        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')

        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    soup, _ = get_soup(
        session=session,
        doc_url=MAIN_DOC_URL
    )

    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserFindTagException(
            'latest_versions: в тегах "ul" не найден раздел "All versions"')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    soup, downloads_url = get_soup(
        session=session,
        doc_url=MAIN_DOC_URL,
        tail_url='download.html'
    )
    table_tag = find_tag(soup, 'table', {'class': 'docutils'})
    epub_tag = find_tag(table_tag, 'a', {'href': re.compile(r'.+html\.zip$')})
    epub_link = epub_tag['href']
    archive_url = urljoin(downloads_url, epub_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    soup, downloads_url = get_soup(
        session=session,
        doc_url=PEP_DOC_URL,
        tail_url='download.html'
    )
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
                soup, _ = get_soup(
                    session=session,
                    doc_url=pep_link
                )
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
        results.append((key, str(value)))

    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()

    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())

    args = arg_parser.parse_args()

    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()

    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode

    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
