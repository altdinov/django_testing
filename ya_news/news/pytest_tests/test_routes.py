from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('url_news_home'),
        pytest.lazy_fixture('url_user_login'),
        pytest.lazy_fixture('url_user_logout'),
        pytest.lazy_fixture('url_user_signup'),
    )
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, url):
    # Главная страница доступна анонимному пользователю.
    # Страницы регистрации пользователей, входа в учётную запись
    # и выхода из неё доступны анонимным пользователям
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_page_availability(url_news_detail, client):
    # Страница отдельной новости доступна анонимному пользователю
    response = client.get(url_news_detail)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('url_comment_edit'),
        pytest.lazy_fixture('url_comment_delete'),
    ),
)
def test_pages_availability_for_different_users(
        parametrized_client, url, expected_status
):
    # Страницы удаления и редактирования комментария доступны автору
    # комментария.
    # Авторизованный пользователь не может зайти на страницы редактирования
    # или удаления чужих комментариев (возвращается ошибка 404)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('url_comment_edit'),
        pytest.lazy_fixture('url_comment_delete'),
    ),
)
@pytest.mark.django_db
def test_redirects(url, url_user_login, client):
    # При попытке перейти на страницу редактирования или удаления
    # комментария анонимный пользователь перенаправляется на
    # страницу авторизации
    expected_url = f'{url_user_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
