from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    """Тесты маршрутизации в web приложении YaNote."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры для класса."""
        cls.author = User.objects.create(username='David')
        cls.reader = User.objects.create(username='Reader Simple')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug1',
            author=cls.author
        )

    def test_pages_availability_anonymous(self):
        """Тестируем страницы, доступные анонимным пользователям."""
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_auth(self):
        """Тестируем страницы, доступные авторизованным пользователям."""
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )

        self.client.force_login(self.author)

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
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
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
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
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
