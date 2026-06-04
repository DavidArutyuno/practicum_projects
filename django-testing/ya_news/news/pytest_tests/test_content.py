import pytest

from news.forms import CommentForm
from news.pytest_tests import settings as s


@pytest.mark.usefixtures('list_news')
def test_news_count(client):
    """Проверка количества новостей на главной."""
    response = client.get(s.URL_NEWS_HOME)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == s.NEWS_COUNT


@pytest.mark.usefixtures('list_news')
def test_news_order(client):
    """Проверка сортировки новостей по дате."""
    response = client.get(s.URL_NEWS_HOME)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_news_detail')),
    )
)
@pytest.mark.usefixtures('few_comments')
def test_comments_order(news, url, client):
    """Проверка сортировки комментариев по дате."""
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'parametrized_client, form_visible',
    (
        (pytest.lazy_fixture('author_client'), True),
    )
)
@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_news_detail')),
    )
)
def test_pages_contains_form_author_client(
    parametrized_client,
    form_visible,
    news,
    url
):
    """
    Доступность формы.

    Проверка доступности формы отправки комментария для анонима и
    авторизованного пользователя.
    """
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_visible
    if form_visible:
        assert isinstance(response.context['form'], CommentForm)


@pytest.mark.parametrize(
    'parametrized_client, form_visible',
    (
        (pytest.lazy_fixture('client'), False),
    )
)
@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_news_detail')),
    )
)
def test_pages_contains_form_anonym_client(
    parametrized_client,
    form_visible,
    news,
    url
):
    """
    Доступность формы.

    Проверка доступности формы отправки комментария для анонима и
    авторизованного пользователя.
    """
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_visible
    if form_visible:
        assert isinstance(response.context['form'], CommentForm)
