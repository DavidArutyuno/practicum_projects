from datetime import datetime, timedelta

from django.test.client import Client
from django.urls import reverse
from django.utils import timezone
import pytest

from news.models import Comment, News
from news.pytest_tests import settings as s


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db,):
    """Доступ к базе данных для всех тестов."""
    ...


@pytest.fixture
def author(django_user_model):
    """Создание пользователя - "автора"."""
    return django_user_model.objects.create(username=s.AUTHOR)


@pytest.fixture
def not_author(django_user_model):
    """Создание пользователя - "не автора"."""
    return django_user_model.objects.create(username=s.NOT_AUTHOR)


@pytest.fixture
def author_client(author):
    """Авторизация пользователя - "автора"."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Авторизация пользователя - "не автора"."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Создание новости в базе данных."""
    return News.objects.create(
        title=s.NEWS_TITLE,
        text=s.NEWS_TEXT
    )


@pytest.fixture
def comment(author, news):
    """Создание комментария к новости в БД."""
    return Comment.objects.create(
        news=news,
        author=author,
        text=s.COMMENT_TEXT
    )


@pytest.fixture
def list_news():
    """Создание нескольких новостей в БД."""
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'{s.NEWS_TITLE} {index}',
            text=f'{s.NEWS_TEXT}',
            date=today - timedelta(days=index)
        )
        for index in range(s.NEWS_COUNT + 2)
    )


@pytest.fixture
def few_comments(news, author):
    """Создание нескольких авторских комментариев к новости в БД."""
    now = timezone.now()
    for index in range(s.COMMENTS_COUNT):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'{s.COMMENT_TEXT} {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return Comment.objects.all()


@pytest.fixture
def url_news_detail(news):
    """Возврат URL NAMESPACE_NEWS_DETAIL по news.pk."""
    return reverse(s.NAMESPACE_NEWS_DETAIL, args=(news.pk,))


@pytest.fixture
def url_news_comment_detail(comment):
    """Возврат URL NAMESPACE_NEWS_DETAIL по comment.pk."""
    return reverse(s.NAMESPACE_NEWS_DETAIL, args=(comment.pk,))


@pytest.fixture
def url_news_comment_edit(comment):
    """Возврат URL NAMESPACE_NEWS_EDIT по comment.pk."""
    return reverse(s.NAMESPACE_NEWS_EDIT, args=(comment.pk,))


@pytest.fixture
def url_news_comment_delete(comment):
    """Возврат URL NAMESPACE_NEWS_DELETE по comment.pk."""
    return reverse(s.NAMESPACE_NEWS_DELETE, args=(comment.pk,))
