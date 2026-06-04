from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note
from notes.tests.settings import ClassTestMixin


User = get_user_model()


class TestListNotes(ClassTestMixin):
    """Тесты отображения заметок на страницах."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры для тестирования."""
        super().setUpTestData()
        cls.users = []
        cls.users.append(cls.author)
        cls.users.append(cls.reader)
        cls.assert_detail_slug = f'{cls.users[0]}-slug-0'

        cls.author_client = Client()

        for user in cls.users:
            Note.objects.bulk_create(
                Note(
                    title=f'Заметка {index} от автора {user}',
                    text=f'Просто текст {index} от автора {user}',
                    slug=f'{user}-slug-{index}',
                    author=user
                )
                for index in range(cls.COUNT_NOTES)
            )

    def test_detail_note_in_object_list(self):
        """
        Отдельная заметка.

        Отдельная заметка передаётся на страницу со списком заметок
        в списке object_list в словаре context.
        """
        self.client.force_login(self.users[0])
        response = self.client.get(self.URL_NOTES_LIST)
        self.assertIn('object_list', response.context)

        notes = response.context['object_list']
        slugs = []
        for note in notes:
            slugs.append(note.slug)
        self.assertIn(self.assert_detail_slug, slugs)

    def test_note_different_authors(self):
        """
        Списки заметок пользователей.

        В список заметок одного пользователя
        не попадают заметки другого пользователя.

        Проверяется количество тестовых заметок: ожидается 5.
        Проверяется содержимое поля slug:
            строка не содержит username пользователя не автора заметки.
        """
        self.author_client.force_login(self.users[0])

        response_author = self.author_client.get(self.URL_NOTES_LIST)
        self.assertIn('object_list', response_author.context)

        notes_author = response_author.context['object_list']
        self.assertEqual(len(notes_author), self.COUNT_NOTES)

        for note_author in notes_author:
            self.assertNotIn(str(self.users[1]), note_author.slug)


class TestDetailPage(ClassTestMixin):
    """
    Формы на страницах.

    Тест передачи форм на страницах создания и редактирования заметок
    для авторизованных пользователей.
    """

    @classmethod
    def setUpTestData(cls):
        """Фикстуры для класса."""
        super().setUpTestData()
        cls.note = Note.objects.create(
            title=f'Заголовок автора {cls.author}',
            text=f'Текст автора {cls.author}',
            slug=f'{cls.author}-slug1',
            author=cls.author
        )

    def test_authorized_client_has_form(self):
        """
        Создание и редактирование заметок.

        На страницы создания и редактирования заметок передаются формы.
        """
        urls = (
            (self.NAMESPACE_NOTES_ADD, None),
            (self.NAMESPACE_NOTES_EDIT, (self.note.slug,)),
        )
        self.client.force_login(self.author)

        for name, args in urls:
            with self.subTest(name=name, args=args):
                response = self.client.get(reverse(name, args=args))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
