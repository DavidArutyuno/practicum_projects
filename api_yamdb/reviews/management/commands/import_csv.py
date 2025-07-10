import csv

from django.core.management.base import BaseCommand

from api_yamdb.settings import CSV_DIR
from reviews import models


DATA_FILES_ORDERED = [
    'category.csv',
    'genre.csv',
    ('titles.csv', 'genre-title.csv'),
    'users.csv',
    'review.csv',
    'comments.csv',
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for file_name in DATA_FILES_ORDERED:
            print(file_name)
            with open(CSV_DIR / file_name, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                if file_name == 'category.csv':
                    self.import_category_genre(reader, models.Category)
                elif file_name == 'genre.csv':
                    self.import_category_genre(reader, models.Genre)

    def import_category_genre(self, reader, model):
        list = []
        existing_ids_slugs = model.objects.values_list('id', 'slug')
        label = model._meta.verbose_name
        for row in reader:
            if row[0] == 'id':
                continue
            if (int(row[0]), row[2]) in existing_ids_slugs:
                print(f'{label} {row[2]} уже существует')
                continue
            list.append(model(
                id=row[0],
                name=row[1],
                slug=row[2]
            ))
        model.objects.bulk_create(list)
