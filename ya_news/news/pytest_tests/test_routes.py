import pytest
from pytest_django.asserts import assertRedirects

from http import HTTPStatus

from django.urls import reverse

from news.pytest_tests import settings as s


@pytest.mark.parametrize(
    'name, args',
    (
        (s.NEWS_HOME, None),
        (s.NEWS_DETAIL, pytest.lazy_fixture('id_for_args')),
        (s.USERS_LOGIN, None),
        (s.USERS_LOGOUT, None),
        (s.USERS_SIGNUP, None),
    ),
)

def test_pages_availability_for_anonymous_user(client, name, args):
    """Анониму доступны страницы."""
    url = reverse(name, args=args)
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
    'name',
    (s.NEWS_EDIT, s.NEWS_DELETE),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, comment, expected_status
):
    """
    Редактирование и удаление комментариев.

    Проверка ответа сервера на нажатие "кнопок" редактирования и
    удаления комментария для разных категорий пользователей.
    """
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    (
        s.NEWS_EDIT,
        s.NEWS_DELETE
    ),
)
def test_redirect_for_anonymous_client(name, client, comment):
    """
    Редиректы.

    Проверка переадресации для анонимных пользователей
    на страницах удаления/редактирования комментариев.
    """
    login_url = reverse(s.USERS_LOGIN)
    url = reverse(name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
