from datetime import datetime, timedelta
import pytest

# Импортируем класс клиента.
from django.test.client import Client
from django.utils import timezone

# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import Comment, News
from news.pytest_tests import settings as s


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db,):
    """Доступ к базе данных для всех тестов."""
    ...


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username=s.AUTHOR)


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username=s.NOT_AUTHOR)


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news():
    """Создаем новость в базе данных"""
    return News.objects.create(
        title=s.NEWS_TITLE,
        text=s.NEWS_TEXT
    )


@pytest.fixture
def comment(author, news):
    """Создаем комментарий к новости"""
    return Comment.objects.create(
        news=news,
        author=author,
        text=s.COMMENT_TEXT
    )


@pytest.fixture
# Фикстура запрашивает другую фикстуру создания заметки.
def id_for_args(news):
    # И возвращает кортеж, который содержит slug заметки.
    # На то, что это кортеж, указывает запятая в конце выражения.
    return (news.id,)


@pytest.fixture
def list_news():
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'{s.NEWS_TITLE} {index}',
            text=f'{s.NEWS_TEXT}',
            # Для каждой новости уменьшаем дату на index дней от today,
            # где index - счётчик цикла.
            date=today - timedelta(days=index)
        )
        for index in range(s.NEWS_COUNT + 2)
    )


@pytest.fixture
def few_comments(news, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'{s.COMMENT_TEXT} {index}',
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        comment.save()
    return Comment.objects.all()


# Добавляем фикстуру form_data
@pytest.fixture
def form_data():
    return {
        'title': f'Новый {s.NEWS_TITLE}',
        'text': f'Новый {s.NEWS_TEXT}'
    }
