from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_pages_availability(self):
        # Главная страница доступна анонимному пользователю
        # Страницы регистрации пользователей, входа в учётную запись и
        # выхода из неё доступны всем пользователям
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for url in urls:
            with self.subTest():
                url = reverse(url)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        # Аутентифицированному пользователю доступна страница со списком
        # заметок notes/, страница успешного добавления заметки done/,
        # страница добавления новой заметки add/.
        urls = (
            'notes:list',
            'notes:add',
            'notes:success',
        )
        for url in urls:
            with self.subTest():
                url = reverse(url)
                self.client.force_login(self.reader)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        # Страницы отдельной заметки, удаления и редактирования заметки
        # доступнытолько автору заметки. Если на эти страницы попытается
        # зайти другой пользователь — вернётся ошибка 404.
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

    def test_redirect(self):
        # При попытке перейти на страницу списка заметок, страницу
        # успешного добавления записи, страницу добавления заметки,
        # отдельной заметки, редактирования или удаления заметки
        # анонимный пользователь перенаправляется на страницу логина.
        login_url = reverse('users:login')
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
