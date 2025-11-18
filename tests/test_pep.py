import inspect

import scrapy

try:
    from pep_parse.spiders.pep import PepSpider
except ModuleNotFoundError:
    raise AssertionError('Не найден файл `pep.py`')
except ImportError as exc:
    raise AssertionError(
        f'Не найден класс `{exc.args[0].split()[3]}` в файле {exc.name}',
    )


def test_pep_spider():
    assert inspect.isclass(PepSpider), (
        '`PepSpider` должен быть классом.'
    )
    assert issubclass(PepSpider, scrapy.Spider), (
        '`PepSpider` должен наследоваться от `scrapy.Spider`'
    )


def test_pep_spider_attrs():
    assert PepSpider.name, (
        'Класс `PepSpider` должен иметь атрибут `name`.'
    )
    assert PepSpider.name == 'pep', (
        'Значением атрибута `name` класса `PepSpider` лучше задать `pep`'
    )
    assert hasattr(PepSpider, 'start_urls'), (
        'Класс `PepSpider` должен иметь атрибут `start_urls`.'
    )
    assert (
        PepSpider.start_urls in (
            ['https://peps.python.org/'],
            ['https://peps.python.org/numerical/']
        )
    ), (
        'Убедитечь, что значение атрибута `start_urls` в классе `PepSpider` - '
        'это список, единственным элементом которого является строка '
        '`https://peps.python.org/` или `https://peps.python.org/numerical/`.'
    )


def test_pep_spider_parse():
    assert hasattr(PepSpider, 'parse'), (
        f'Класс `{PepSpider.__class__.__name__}` должен иметь метод `parse`.'
    )
    assert callable(PepSpider.parse), (
        f'Убедитесь, что `parse` в классе {PepSpider.__class__.__name__} '
        '- это вызываемый метод.'
    )


def test_pep_spider_parse_pep():
    assert hasattr(PepSpider, 'parse_pep'), (
        f'В классе `{PepSpider.__class__.__name__}` должен быть метод '
        '`parse_pep`.'
    )
    assert callable(PepSpider.parse_pep), (
        f'Убедитесь, что `parse_pep` в классе {PepSpider.__class__.__name__} '
        '- это вызываемый метод.'
    )
