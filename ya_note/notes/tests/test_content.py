from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestListNotes(TestCase):
    """Тесты отображения заметок на страницах."""

    LIST_NOTES_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        """Фикстуры для класса."""
        cls.authors = []
        cls.authors.append(User.objects.create(username='David'))
        cls.authors.append(User.objects.create(username='LeeSu'))
        cls.url_detail_slug = f'{cls.authors[0]}-slug-0'

        # Создаём объект клиента.
        cls.author_1_client = Client()
        cls.author_2_client = Client()

        for cls_author in cls.authors:
            Note.objects.bulk_create(
                Note(
                    title=f'Заметка {index} от автора {cls_author}',
                    text=f'Просто текст {index} от автора {cls_author}',
                    slug=f'{cls_author}-slug-{index}',
                    author=cls_author
                )
                for index in range(5)
            )

    def test_detail_note_in_object_list(self):
        """
        Отдельная заметка.

        Отдельная заметка передаётся на страницу со списком заметок
        в списке object_list в словаре context.
        """
        self.client.force_login(self.authors[0])
        response = self.client.get(self.LIST_NOTES_URL)
        self.assertIn('object_list', response.context)

        notes = response.context['object_list']
        all_slugs = []
        for note in notes:
            all_slugs.append(note.slug)
        self.assertIn(self.url_detail_slug, all_slugs)

    def test_note_different_authors(self):
        """
        Списки заметок пользователей.

        В список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        self.author_1_client.force_login(self.authors[0])
        self.author_2_client.force_login(self.authors[1])

        response_author_1 = self.author_1_client.get(self.LIST_NOTES_URL)
        response_author_2 = self.author_2_client.get(self.LIST_NOTES_URL)

        self.assertIn('object_list', response_author_1.context)
        self.assertIn('object_list', response_author_2.context)

        notes_author_1 = response_author_1.context['object_list']
        notes_author_2 = response_author_2.context['object_list']

        slugs_author_1 = []
        slugs_author_2 = []
        for note in notes_author_1:
            slugs_author_1.append(note.slug)
        for note in notes_author_2:
            slugs_author_2.append(note.slug)
        self.assertNotEqual(slugs_author_1, slugs_author_2)


class TestDetailPage(TestCase):
    """
    Формы на страницах.

    Тест передачи форм на страницах создания и редактирования заметок
    для авторизованных пользователей.
    """

    @classmethod
    def setUpTestData(cls):
        """Фикстуры для класса."""
        cls.author = User.objects.create(username='David')
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
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        self.client.force_login(self.author)

        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
