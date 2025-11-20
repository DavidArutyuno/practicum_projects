import scrapy

from pep_parse.items import PepParseItem
from pep_parse.settings import ALLOWED_DOMAINS, START_URLS


class PepSpider(scrapy.Spider):
    name = 'pep'
    allowed_domains = ALLOWED_DOMAINS
    start_urls = START_URLS

    def parse(self, response):
        """
        Парсит главную страницу и собирает ссылки на PEP.

        Находим все ссылки на PEP в секции index-by-category.
        В списке перебираем каждую найденную ссылку и передаем на выполнение
        в функцию parse_pep().
        """
        pep_text = 'pep-'
        pep_links = response.css(
            f'section#index-by-category '
            f'a[href^={pep_text}]::attr(href)'
        ).getall()

        for pep_link in pep_links:
            yield response.follow(
                pep_link,
                callback=self.parse_pep
            )

    def parse_pep(self, response):
        """
        Парсит страницу отдельного PEP.

        Извлекаем номер PEP из заголовка.
        В цикле:
            извлекаем номер из формата "PEP XXX – Название",
            Извлекаем название (всё что после "PEP XXX – ").
        Извлекаем статус PEP:
            ищем <dt> с текстом "Status" и берем следующий <dd>.
        Создаем и возвращаем Item.
        """

        title = response.css('h1.page-title::text').get()
        if title and 'PEP' in title:
            pep_number = title.split()[1]
            name_parts = title.split(' – ', 1)
            if len(name_parts) > 1:
                name = name_parts[1].strip()
        status_text = 'Status'
        status = response.css(f'dt:contains({status_text}) + dd ::text').get()

        item = {
            'number': pep_number,
            'name': name,
            'status': status.strip() if status else 'Unknown'
        }

        yield PepParseItem(item)
