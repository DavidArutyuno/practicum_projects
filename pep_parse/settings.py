import os
from pathlib import Path

BOT_NAME = 'pep_parse'

SPIDER_MODULES = ['pep_parse.spiders']
NEWSPIDER_MODULE = 'pep_parse.spiders'

BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / 'results'
FEED_EXPORT_ENCODING = "utf-8"
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
ALLOWED_DOMAINS = ['peps.python.org']
START_URLS = ['https://peps.python.org/']

FEEDS = {
    'results/pep_%(time)s.csv': {
        'format': 'csv',
        'fields': ['number', 'name', 'status'],
        'encoding': FEED_EXPORT_ENCODING,
        'overwrite': True
    }
}

ITEM_PIPELINES = {
    'pep_parse.pipelines.PepParsePipeline': 300,
}
