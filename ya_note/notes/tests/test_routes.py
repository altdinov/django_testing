from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

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
        cls.URL_NOTES_HOME = reverse('notes:home')
        cls.URL_USERS_LOGIN = reverse('users:login')
        cls.URL_USERS_LOGOUT = reverse('users:logout')
        cls.URL_USERS_SIGNUP = reverse('users:signup')
        cls.URL_NOTES_LIST = reverse('notes:list')
        cls.URL_NOTES_ADD = reverse('notes:add')
        cls.URL_NOTES_SUCCESS = reverse('notes:success')
        cls.URL_NOTES_DETAIL = reverse('notes:detail', args=(cls.note.slug,))
        cls.URL_NOTES_EDIT = reverse('notes:edit', args=(cls.note.slug,))
        cls.URL_NOTES_DELETE = reverse('notes:delete', args=(cls.note.slug,))

    def test_pages_availability(self):
        # Главная страница доступна анонимному пользователю
        # Страницы регистрации пользователей, входа в учётную запись и
        # выхода из неё доступны всем пользователям
        urls = (
            self.URL_NOTES_HOME,
            self.URL_USERS_LOGIN,
            self.URL_USERS_LOGOUT,
            self.URL_USERS_SIGNUP,
        )
        for url in urls:
            with self.subTest():
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        # Аутентифицированному пользователю доступна страница со списком
        # заметок notes/, страница успешного добавления заметки done/,
        # страница добавления новой заметки add/
        urls = (
            self.URL_NOTES_LIST,
            self.URL_NOTES_ADD,
            self.URL_NOTES_SUCCESS,
        )
        for url in urls:
            with self.subTest():
                response = self.reader_logged.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        # Страницы отдельной заметки, удаления и редактирования заметки
        # доступнытолько автору заметки. Если на эти страницы попытается
        # зайти другой пользователь — вернётся ошибка 404
        users_statuses = (
            (self.author_logged, HTTPStatus.OK),
            (self.reader_logged, HTTPStatus.NOT_FOUND),
        )
        for client, status in users_statuses:
            for url in (
                self.URL_NOTES_DETAIL,
                self.URL_NOTES_EDIT,
                self.URL_NOTES_DELETE
            ):
                with self.subTest():
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect(self):
        # При попытке перейти на страницу списка заметок, страницу
        # успешного добавления записи, страницу добавления заметки,
        # отдельной заметки, редактирования или удаления заметки
        # анонимный пользователь перенаправляется на страницу логина
        urls = (
            self.URL_NOTES_DETAIL,
            self.URL_NOTES_EDIT,
            self.URL_NOTES_DELETE,
            self.URL_NOTES_ADD,
            self.URL_NOTES_SUCCESS,
            self.URL_NOTES_LIST,
        )
        for url in urls:
            with self.subTest():
                redirect_url = f'{self.URL_USERS_LOGIN}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
