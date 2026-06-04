from http import HTTPStatus

from django.contrib.auth import get_user_model

from notes.models import Note
from notes.tests.settings import ClassTestMixin


User = get_user_model()


class TestRoutes(ClassTestMixin):
    """Тесты маршрутизации в web приложении YaNote."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры для тестирования."""
        super().setUpTestData()
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author,
        )

    def test_pages_availability_anonymous(self):
        """Тестируем страницы, доступные анонимным пользователям."""
        urls = (
            (self.URL_NOTES_HOME),
            (self.URL_USERS_LOGIN),
            (self.URL_USERS_LOGOUT),
            (self.URL_USERS_SIGNUP),
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_auth(self):
        """Тестируем страницы, доступные авторизованным пользователям."""
        urls = (
            (self.URL_NOTES_LIST),
            (self.URL_NOTES_SUCCESS),
            (self.URL_NOTES_ADD),
        )

        self.client.force_login(self.author)

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_detail_edit_delete(self):
        """
        Доступность страниц.

        Отдельная заметка, редактирование и удаление
        доступны или недоступны автору/ не автору заметки.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for url in (
                self.URL_NOTES_DETAIL,
                self.URL_NOTES_EDIT,
                self.URL_NOTES_DELETE
            ):
                with self.subTest(user=user, url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        Перенаправления.

        При попытке перейти на
            страницу списка заметок,
            страницу успешного добавления записи,
            страницу добавления заметки,
            отдельной заметки,
            редактирования или
            удаления заметки -
        анонимный пользователь перенаправляется на страницу логина.
        """
        urls = (
            (self.URL_NOTES_LIST),
            (self.URL_NOTES_SUCCESS),
            (self.URL_NOTES_ADD),
            (self.URL_NOTES_DETAIL),
            (self.URL_NOTES_EDIT),
            (self.URL_NOTES_DELETE),
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertRedirects(
                    self.client.get(url),
                    self.REDIRECT_TEMPLATE.substitute({'url': url})
                )
