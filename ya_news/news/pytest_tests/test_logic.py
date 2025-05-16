from http import HTTPStatus

import pytest

from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from news.pytest_tests import settings as s


def test_anonymous_user_cant_create_comment(client, news):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse(s.NEWS_DETAIL, args=(news.id,))
    client.post(url, data={'text': s.COMMENT_TEXT})
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, news):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse(s.NEWS_DETAIL, args=(news.pk,))
    response = author_client.post(url, data={'text': s.COMMENT_TEXT})
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == s.COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize(
    'bad_words',
    (f'Какой-то текст, {bad_word}, еще текст' for bad_word in BAD_WORDS),
)
def test_user_cant_use_bad_words(bad_words, author_client, news):
    """
    Цензура.

    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    url = reverse(s.NEWS_DETAIL, args=(news.id,))
    response = author_client.post(url, data={'text': bad_words})
    form = response.context['form']
    assertFormError(
        form=form,
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(comment, author_client):
    """Автор может удалять свои комментарии."""
    delete_url = reverse(s.NEWS_DELETE, args=(comment.id,))
    response = author_client.delete(delete_url)
    url_to_comments = reverse(s.NEWS_DETAIL,
                              args=(comment.id,))
    assertRedirects(response, url_to_comments + '#comments')
    # Проверим статус-код ответа
    assert response.status_code == HTTPStatus.FOUND
    # Проверим количество комментариев стало 0
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
        comment, not_author_client
):
    """Пользователь не может удалить чужой комментарий."""
    delete_url = reverse(s.NEWS_DELETE, args=(comment.id,))
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(news, comment, author_client, author):
    """Автор комментария может его отредактировать."""
    edit_url = reverse(s.NEWS_EDIT, args=(comment.pk,))
    response = author_client.post(edit_url,
                                  data={'text': s.NEW_COMMENT_TEXT})
    url_to_comments = reverse(s.NEWS_DETAIL, args=(comment.id,))
    assertRedirects(response, url_to_comments + '#comments')
    comment.refresh_from_db()
    assert comment.text == s.NEW_COMMENT_TEXT
    assert comment.author == author
    assert comment.news == news


def test_user_cant_edit_comment_of_another_user(
        news, comment, not_author_client, author
):
    """Пользователь не может редактировать чужие комментарии."""
    edit_url = reverse(s.NEWS_EDIT, args=(comment.pk,))
    response = not_author_client.post(edit_url,
                                      data={'text': s.NEW_COMMENT_TEXT})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == s.COMMENT_TEXT
    assert comment.author == author
    assert comment.news == news
