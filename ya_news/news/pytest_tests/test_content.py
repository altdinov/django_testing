import pytest
from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_news_count(eleven_news, client):
    # Количество новостей на главной странице — не более 10.
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(eleven_news, client):
    # Новости отсортированы от самой свежей к самой старой.
    # Свежие новости в начале списка.
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(news_with_two_comments, client):
    # Комментарии на странице отдельной новости отсортированы в хронологическом
    # порядке: старые в начале списка, новые — в конце.
    detail_url = reverse('news:detail', args=(news_with_two_comments.id,))
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(news, client):
    # Анонимному пользователю недоступна форма для отправки комментария на
    # странице отдельной новости
    detail_url = reverse('news:detail', args=(news.id,))
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(news, author_client):
    # Авторизованному пользователю доступна форма для отправки комментария на
    # странице отдельной новости
    detail_url = reverse('news:detail', args=(news.id,))
    response = author_client.get(detail_url)
    assert 'form' in response.context
