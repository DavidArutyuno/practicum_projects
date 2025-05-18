from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from news.pytest_tests import settings as s


@pytest.mark.parametrize(
    'url',
    (
        s.URL_NEWS_HOME,
        pytest.lazy_fixture('url_news_detail'),
        s.URL_USERS_LOGIN,
        s.URL_USERS_LOGOUT,
        s.URL_USERS_SIGNUP,
    ),
)
def test_pages_availability_for_anonymous_user(client, url):
    """Анониму доступны страницы."""
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('url_news_comment_edit'),
        pytest.lazy_fixture('url_news_comment_delete')
    ),
)
def test_pages_availability_for_different_users(
        parametrized_client, url, expected_status
):
    """
    Редактирование и удаление комментариев.

    Проверка ответа сервера на нажатие "кнопок" редактирования и
    удаления комментария для разных категорий пользователей.
    """
    # url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('url_news_comment_edit'),
        pytest.lazy_fixture('url_news_comment_delete')
    ),
)
def test_redirect_for_anonymous_client(url, client):
    """
    Редиректы.

    Проверка переадресации для анонимных пользователей
    на страницах удаления/редактирования комментариев.
    """
    expected_url = f'{s.URL_USERS_LOGIN}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
