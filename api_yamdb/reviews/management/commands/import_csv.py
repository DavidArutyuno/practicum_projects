"""
Management-команда для импорта данных из CSV-файлов в базу данных.
Порядок импорта данных важен.

Использование:
    python manage.py import_csv

Команда импортирует данные из следующих файлов в папке static/data/:
    - category.csv - категории произведений
    - genre.csv - жанры произведений
    - titles.csv - произведения
    - genre_title.csv - связь произведение-жанр
    - users.csv - пользователи
    - review.csv - отзывы к произведениям
    - comments.csv - комментарии к отзывам

Общий алгоритм:
    1. Собираем данные из csv-файла
    2. Выгружаем данные из БД
    3. Проверяем согласованность данных из csv-файла и БД
    4. Импортируем данные в БД
"""

import csv
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Q

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title

from api_yamdb.settings import CSV_DIR


User = get_user_model()

DATA_FILES_ORDERED = [
    'category.csv',
    'genre.csv',
    'titles.csv',
    'genre_title.csv',
    'users.csv',
    'review.csv',
    'comments.csv',
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(f'Импорт данных из {CSV_DIR}...')
        for file_name in DATA_FILES_ORDERED:
            print(f'Импорт данных из {file_name}...')
            with open(CSV_DIR / file_name, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                match file_name:
                    case 'category.csv':
                        self.import_category_genre(reader, Category)
                    case 'genre.csv':
                        self.import_category_genre(reader, Genre)
                    case 'titles.csv':
                        self.import_titles(reader)
                    case 'genre_title.csv':
                        self.import_genre_title(reader)
                    case 'users.csv':
                        self.import_users(reader)
                    case 'review.csv':
                        self.import_reviews(reader)
                    case 'comments.csv':
                        self.import_comments(reader)
            print(f'Импорт из {file_name} завершен')
        print('Импорт данных завершен')

    def import_category_genre(self, reader, model):
        models_to_create = []
        needed_ids = set()
        needed_slugs = set()
        label = model._meta.verbose_name
        rows_to_process = []

        for row in reader:
            if row[0] == 'id':
                continue
            needed_ids.add(int(row[0]))
            needed_slugs.add(row[2])
            rows_to_process.append(row)

        existing_data = model.objects.filter(
            Q(id__in=needed_ids)
            | Q(slug__in=needed_slugs)
        ).values_list('id', 'slug')
        existing_ids = {row[0] for row in existing_data}
        existing_slugs = {row[1] for row in existing_data}

        for row in rows_to_process:
            if int(row[0]) in existing_ids:
                print(f'{label} с id {row[0]} уже существует')
                print(f'    {label} {row[1]} не будет импортирован')
                continue
            if row[2] in existing_slugs:
                print(f'{label} с slug {row[2]} уже существует')
                print(f'    {label} {row[1]} не будет импортирован')
                continue
            models_to_create.append(
                model(
                    id=row[0],
                    name=row[1],
                    slug=row[2]
                )
            )

        model.objects.bulk_create(models_to_create)

    def import_titles(self, reader):
        titles_to_create = []
        needed_ids = set()
        needed_category_ids = set()
        rows_to_process = []

        for row in reader:
            if row[0] == 'id':
                continue
            needed_ids.add(int(row[0]))
            category_id = int(row[3]) if row[3] else None
            if category_id:
                needed_category_ids.add(category_id)
            rows_to_process.append(row)

        existing_ids = Title.objects.filter(id__in=needed_ids).values_list(
            'id', flat=True)
        categories = {
            cat.id: cat for cat in Category.objects.filter(
                id__in=needed_category_ids)
        }

        for row in rows_to_process:
            if int(row[0]) in existing_ids:
                print(f'Произведение с id {row[0]} уже существует')
                print(f'    Произведение {row[1]} не будет импортировано')
                continue
            category_id = int(row[3]) if row[3] else None
            category = categories.get(category_id) if category_id else None
            if category_id and not category:
                print(f'Категория с id {category_id} не найдена')
                print(f'    Произведение {row[1]} не будет импортировано')
                continue
            titles_to_create.append(
                Title(
                    id=row[0],
                    name=row[1],
                    year=row[2],
                    category=category
                )
            )

        Title.objects.bulk_create(titles_to_create)

    def import_genre_title(self, reader):
        genre_titles = []
        needed_pairs = set()
        needed_title_ids = set()
        needed_genre_ids = set()
        rows_to_process = []

        for row in reader:
            if row[0] == 'id':
                continue
            title_id = int(row[1])
            genre_id = int(row[2])
            needed_pairs.add((title_id, genre_id))
            needed_title_ids.add(title_id)
            needed_genre_ids.add(genre_id)
            rows_to_process.append(row)

        existing_relations = set(
            GenreTitle.objects.filter(
                title_id__in=needed_title_ids,
                genre_id__in=needed_genre_ids
            ).values_list('title_id', 'genre_id')
        )
        existing_title_ids = set(
            Title.objects.filter(id__in=needed_title_ids).values_list(
                'id', flat=True)
        )
        existing_genre_ids = set(
            Genre.objects.filter(id__in=needed_genre_ids).values_list(
                'id', flat=True)
        )

        for row in rows_to_process:
            title_id = int(row[1])
            genre_id = int(row[2])
            if (title_id, genre_id) in existing_relations:
                print(f'Связь title_id={title_id}, '
                      f'genre_id={genre_id} уже существует')
                print('    Связь не будет импортирована')
                continue
            if title_id not in existing_title_ids:
                print(f'Произведение с id {title_id} не найдено')
                print('    Связь не будет импортирована')
                continue
            if genre_id not in existing_genre_ids:
                print(f'Жанр с id {genre_id} не найден')
                print('    Связь не будет импортирована')
                continue
            genre_titles.append(
                GenreTitle(
                    title_id=title_id,
                    genre_id=genre_id
                )
            )

        GenreTitle.objects.bulk_create(genre_titles)

    def import_users(self, reader):
        users_to_save = []
        rows_to_process = []
        needed_ids = set()
        needed_emails = set()
        needed_usernames = set()

        for row in reader:
            if row[0] == 'id':
                continue
            needed_ids.add(int(row[0]))
            needed_emails.add(row[2])
            needed_usernames.add(row[1])
            rows_to_process.append(row)

        existing_users = User.objects.filter(
            Q(id__in=needed_ids)
            | Q(email__in=needed_emails)
            | Q(username__in=needed_usernames)
        ).values_list('id', 'email', 'username')
        existing_ids = {row[0] for row in existing_users}
        existing_emails = {row[1] for row in existing_users}
        existing_usernames = {row[2] for row in existing_users}

        for row in rows_to_process:
            if int(row[0]) in existing_ids:
                print(f'Пользователь с id {row[0]} уже существует')
                print(f'    Пользователь {row[1]} не будет импортирован')
                continue
            if row[2] in existing_emails:
                print(f'Пользователь с email {row[2]} уже существует')
                print(f'    Пользователь {row[1]} не будет импортирован')
                continue
            if row[1] in existing_usernames:
                print(f'Пользователь с username {row[1]} уже существует')
                print(f'    Пользователь {row[1]} не будет импортирован')
                continue
            user = User(
                id=row[0],
                username=row[1],
                role=row[3],
                bio=row[4] if row[4] else '',
                first_name=row[5] if row[5] else '',
                last_name=row[6] if row[6] else ''
            )
            user.email = row[2]
            users_to_save.append(user)

        User.objects.bulk_create(users_to_save)

    def import_reviews(self, reader):
        reviews_to_save = []
        rows_to_process = []
        needed_ids = set()
        needed_title_ids = set()
        needed_author_ids = set()

        for row in reader:
            if row[0] == 'id':
                continue
            needed_ids.add(int(row[0]))
            needed_title_ids.add(int(row[1]))
            needed_author_ids.add(int(row[3]))
            rows_to_process.append(row)

        existing_ids = Review.objects.filter(id__in=needed_ids).values_list(
            'id', flat=True)
        titles = {
            title.id: title for title in Title.objects.filter(
                id__in=needed_title_ids)
        }
        authors = {
            user.id: user for user in User.objects.filter(
                id__in=needed_author_ids)
        }

        for row in rows_to_process:
            if int(row[0]) in existing_ids:
                print(f'Отзыв с id {row[0]} уже существует')
                print(f'    Отзыв {row[2]} не будет импортирован')
                continue
            title = titles.get(int(row[1]))
            author = authors.get(int(row[3]))
            if not title:
                print(f'Произведение с id {int(row[1])} не найдено')
                print(f'    Отзыв {row[2]} не будет импортирован')
                continue
            if not author:
                print(f'Пользователь с id {int(row[3])} не найден')
                print(f'    Отзыв {row[2]} не будет импортирован')
                continue
            pub_date = datetime.fromisoformat(
                row[5].replace('Z', '+00:00')
            )
            reviews_to_save.append(
                Review(
                    id=row[0],
                    title=title,
                    text=row[2],
                    author=author,
                    score=row[4],
                    pub_date=pub_date
                )
            )

        Review.objects.bulk_create(reviews_to_save)

    def import_comments(self, reader):
        comments_to_save = []
        needed_ids = set()
        needed_review_ids = set()
        needed_author_ids = set()
        rows_to_process = []

        for row in reader:
            if row[0] == 'id':
                continue
            needed_ids.add(int(row[0]))
            needed_review_ids.add(int(row[1]))
            needed_author_ids.add(int(row[3]))
            rows_to_process.append(row)

        existing_ids = Comment.objects.filter(id__in=needed_ids).values_list(
            'id', flat=True)
        reviews = {
            review.id: review for review in Review.objects.filter(
                id__in=needed_review_ids
            )
        }
        authors = {
            user.id: user for user in User.objects.filter(
                id__in=needed_author_ids
            )
        }

        for row in rows_to_process:
            if int(row[0]) in existing_ids:
                print(f'Комментарий с id {row[0]} уже существует')
                print(f'    Комментарий {row[2]} не будет импортирован')
                continue
            review_id = int(row[1])
            author_id = int(row[3])
            review = reviews.get(review_id)
            author = authors.get(author_id)
            if not review:
                print(f'Отзыв с id {review_id} не найден')
                print(f'    Комментарий {row[2]} не будет импортирован')
                continue
            if not author:
                print(f'Пользователь с id {author_id} не найден')
                print(f'    Комментарий {row[2]} не будет импортирован')
                continue
            pub_date = datetime.fromisoformat(
                row[4].replace('Z', '+00:00')
            )
            comments_to_save.append(Comment(
                id=row[0],
                review=review,
                text=row[2],
                author=author,
                pub_date=pub_date
            ))

        Comment.objects.bulk_create(comments_to_save)
