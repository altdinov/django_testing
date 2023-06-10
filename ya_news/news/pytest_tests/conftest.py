import random
from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from news.models import Comment, News

COMMENT_TEXT = 'Текст комментария'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def eleven_news():
    today = datetime.today()
    all_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        one_news = News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index),
        )
        all_news.append(one_news)
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT,
    )
    return comment


@pytest.fixture
def news_with_ten_comments(news, author):
    start_date = timezone.now()
    end_date = start_date + timedelta(days=10)
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = (
            start_date + (end_date - start_date) * random.random()
        )
        comment.save()
    return news


@pytest.fixture
def url_news_detail(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def url_comment_delete(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def url_comment_edit(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def url_news_home():
    return reverse('news:home')


@pytest.fixture
def url_user_login():
    return reverse('users:login')


@pytest.fixture
def url_user_logout():
    return reverse('users:logout')


@pytest.fixture
def url_user_signup():
    return reverse('users:signup')
