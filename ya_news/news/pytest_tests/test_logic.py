from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from news.pytest_tests import settings as s


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('url_news_detail'),
    ),
)
def test_anonymous_user_cant_create_comment(
    client,
    url
):
    """Анонимный пользователь не может отправить комментарий."""
    count_comments_start_test = Comment.objects.count()
    client.post(url, data=s.COMMENT_DATA)
    count_comments_end_test = Comment.objects.count()
    assert count_comments_end_test == count_comments_start_test


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('url_news_detail'),
    ),
)
def test_user_can_create_comment(
    author_client,
    author,
    url,
    news
):
    """Авторизованный пользователь может отправить комментарий."""
    count_comments_start_test = Comment.objects.count()
    response = author_client.post(url, data=s.COMMENT_DATA)
    assertRedirects(response, f'{url}#comments')
    count_comments_end_test = Comment.objects.count()
    assert count_comments_end_test == count_comments_start_test + 1

    comment = Comment.objects.last()
    assert comment.text == s.COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_news_detail')),
    )
)
@pytest.mark.parametrize(
    'bad_words',
    (f'Какой-то текст, {bad_word}, еще текст' for bad_word in BAD_WORDS),
)
def test_user_cant_use_bad_words(
    url,
    bad_words,
    author_client
):
    """
    Цензура.

    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    count_comments_start_test = Comment.objects.count()
    response = author_client.post(url, data={'text': bad_words})
    form = response.context['form']
    assertFormError(
        form=form,
        field='text',
        errors=WARNING
    )
    count_comments_end_test = Comment.objects.count()
    assert count_comments_end_test == count_comments_start_test


@pytest.mark.parametrize(
    'url_delete',
    (
        (pytest.lazy_fixture('url_news_comment_delete')),
    )
)
@pytest.mark.parametrize(
    'url_comment_detail',
    (
        (pytest.lazy_fixture('url_news_comment_detail')),
    )
)
def test_author_can_delete_comment(
    author_client,
    url_delete,
    url_comment_detail
):
    """Автор может удалять свои комментарии."""
    count_comments_start_test = Comment.objects.count()
    response = author_client.delete(url_delete)
    assertRedirects(response, url_comment_detail + '#comments')
    assert response.status_code == HTTPStatus.FOUND
    count_comments_end_test = Comment.objects.count()
    assert count_comments_end_test == count_comments_start_test - 1


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_news_comment_delete')),
    )
)
def test_user_cant_delete_comment_of_another_user(
        not_author_client,
        url
):
    """Пользователь не может удалить чужой комментарий."""
    count_comments_start_test = Comment.objects.count()
    response = not_author_client.delete(url)
    count_comments_end_test = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert count_comments_end_test == count_comments_start_test


@pytest.mark.parametrize(
    'url_edit',
    (
        (pytest.lazy_fixture('url_news_comment_edit')),
    )
)
@pytest.mark.parametrize(
    'url_comment_detail',
    (
        (pytest.lazy_fixture('url_news_comment_detail')),
    )
)
def test_author_can_edit_comment(
    news,
    comment,
    author_client,
    author,
    url_edit,
    url_comment_detail

):
    """Автор комментария может его отредактировать."""
    response = author_client.post(url_edit,
                                  data={'text': s.NEW_COMMENT_TEXT})
    assertRedirects(response, url_comment_detail + '#comments')
    comment.refresh_from_db()
    assert comment.text == s.NEW_COMMENT_TEXT
    assert comment.author == author
    assert comment.news == news


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_news_comment_edit')),
    )
)
def test_user_cant_edit_comment_of_another_user(
    news,
    comment,
    not_author_client,
    author,
    url
):
    """Пользователь не может редактировать чужие комментарии."""
    response = not_author_client.post(url,
                                      data={'text': s.NEW_COMMENT_TEXT})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == s.COMMENT_TEXT
    assert comment.author == author
    assert comment.news == news
