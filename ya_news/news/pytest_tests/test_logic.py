from http import HTTPStatus

import pytest
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from news.pytest_tests.conftest import COMMENT_TEXT
from pytest_django.asserts import assertFormError, assertRedirects

NEW_COMMENT_TEXT = 'Новый текст комментария'
form_data = {'text': NEW_COMMENT_TEXT}


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(news, client):
    # Анонимный пользователь не может отправить комментарий
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(news, admin_client):
    # Авторизованный пользователь может отправить комментарий
    url = reverse('news:detail', args=(news.id,))
    response = admin_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_user_cant_use_bad_words(news, admin_client):
    # Если комментарий содержит запрещённые слова, он не будет опубликован,
    # а форма вернёт ошибку
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(comment, news, author_client):
    # Авторизованный пользователь может удалять свои комментарии
    delete_url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(delete_url)
    url = reverse('news:detail', args=(news.id,))
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(comment, admin_client):
    # Авторизованный пользователь не может удалять чужие комментарии.
    delete_url = reverse('news:delete', args=(comment.id,))
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(comment, news, author_client):
    # Авторизованный пользователь может редактировать свои комментарии.
    edit_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(edit_url, data=form_data)
    url = reverse('news:detail', args=(news.id,))
    assertRedirects(response, f'{url}#comments')
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(comment, admin_client):
    # Авторизованный пользователь не может редактировать чужие комментарии.
    edit_url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
