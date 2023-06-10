from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note
from notes.tests.test_routes import User


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_logged = Client()
        cls.reader_logged = Client()
        cls.author_logged.force_login(cls.author)
        cls.reader_logged.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )
        cls.URL_NOTES_LIST = reverse('notes:list')
        cls.URL_NOTES_ADD = reverse('notes:add')
        cls.URL_NOTES_EDIT = reverse('notes:edit', args=(cls.note.slug,))

    def test_notes_list_for_different_users(self):
        # Отдельная заметка передаётся на страницу со списком
        # заметок в списке object_list в словаре context;
        # В список заметок одного пользователя не попадают
        # заметки другого пользователя
        users_statuses = (
            (self.author_logged, True),
            (self.reader_logged, False),
        )
        for user, status in users_statuses:
            with self.subTest():
                response = user.get(self.URL_NOTES_LIST)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, status)

    def test_pages_contains_form(self):
        # На страницы создания и редактирования заметки передаются формы
        urls = (self.URL_NOTES_ADD, self.URL_NOTES_EDIT)
        for url in urls:
            with self.subTest():
                response = self.author_logged.get(url)
                self.assertIn('form', response.context)
