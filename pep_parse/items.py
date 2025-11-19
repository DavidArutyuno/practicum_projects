import scrapy


class PepParseItem(scrapy.Item):
    number = scrapy.Field()  # номер PEP
    name = scrapy.Field()  # название PEP
    status = scrapy.Field()  # статус, указанный на странице PEP
