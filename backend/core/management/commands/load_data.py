import csv
import json
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    """
    Команда для загрузки ингредиентов и тегов из файлов.

    Поддерживает форматы JSON и CSV. Автоматически определяет тип данных
    по структуре файла или можно указать явно через аргументы.
    """

    help = '''
    Загружает ингредиенты и теги из JSON/CSV файлов.

    Примеры использования:
    - python manage.py load_data data/ingredients.json
    - python manage.py load_data data/tags.csv --model=tag
    - python manage.py load_data data/tags.json --model=tag
    - python manage.py load_data data/unknown --format=json --model=ingredient
    '''

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Путь к файлу с данными'
        )
        parser.add_argument(
            '--model',
            type=str,
            choices=['ingredient', 'tag', 'auto'],
            default='auto',
            help='Тип модели для загрузки (auto - автоопределение)'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'csv', 'auto'],
            default='auto',
            help='Формат файла (auto - автоопределение по расширению)'
        )

    def handle(self, *args, **options):
        """Основной метод обработки команды."""
        file_path = options['file_path']
        model_type = options['model']
        file_format = options['format']

        # Автоопределение формата
        if file_format == 'auto':
            file_format = self._detect_file_format(file_path)

        # Автоопределение модели
        if model_type == 'auto':
            model_type = self._detect_model_type(file_path, file_format)

        try:
            if model_type == 'ingredient':
                self._load_ingredients(file_path, file_format)
            elif model_type == 'tag':
                self._load_tags(file_path, file_format)

            self.stdout.write(
                self.style.SUCCESS('Данные успешно загружены')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка загрузки: {str(e)}')
            )

    def _detect_file_format(self, file_path):
        """Определяет формат файла по расширению."""
        extension = Path(file_path).suffix.lower()
        if extension == '.json':
            return 'json'
        elif extension in ['.csv', '.txt']:
            return 'csv'
        else:
            raise ValueError('Не удалось определить формат файла')

    def _detect_model_type(self, file_path, file_format):
        """Определяет тип модели по структуре данных."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_format == 'json':
                    sample_data = json.load(f)[0]
                else:
                    sample_data = next(csv.reader(f))

                # Определяем по полям
                if 'measurement_unit' in sample_data:
                    return 'ingredient'
                elif 'slug' in sample_data:
                    return 'tag'
                else:
                    raise ValueError('Не удалось определить тип данных')

        except (IndexError, StopIteration):
            raise ValueError('Файл пуст или имеет неверный формат')

    def _load_ingredients(self, file_path, file_format):
        """Загружает ингредиенты из файла."""
        if file_format == 'json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    Ingredient.objects.get_or_create(
                        name=item['name'],
                        measurement_unit=item['measurement_unit']
                    )
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Пропускаем заголовок
                for row in reader:
                    if len(row) >= 2:
                        Ingredient.objects.get_or_create(
                            name=row[0],
                            measurement_unit=row[1]
                        )

    def _load_tags(self, file_path, file_format):
        """Загружает теги из файла."""
        if file_format == 'json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    Tag.objects.get_or_create(
                        name=item['name'],
                        slug=item.get('slug', '')  # slug опциональный
                    )
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Пропускаем заголовок
                for row in reader:
                    if len(row) >= 1:
                        Tag.objects.get_or_create(
                            name=row[0],
                            slug=row[1] if len(row) >= 2 else ''
                        )
