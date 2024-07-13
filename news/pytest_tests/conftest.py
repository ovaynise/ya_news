from django.test.client import Client
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta

import pytest

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    """Создаем модель автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Создаем модель авторизованого пользователя."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Создаем клиент автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Создаем клиент авторизованного пользователя."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Создаем объект одной новости."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости 1',
    )
    return news


@pytest.fixture
def comment(author, news):
    """Создаем объект комментария."""
    comment = Comment.objects.create(
        text='Текст комментария 1',
        news=news,
        author=author,
    )
    return comment


@pytest.fixture
def form_data():
    """Создаем словарь с текстом нового комментария."""
    return {
        'text': 'Новый текст',
    }


@pytest.fixture
def many_news():
    """Создаем больше 10 объектов новостей."""
    today = datetime.today()
    many_news = News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return many_news


@pytest.fixture
def comments(news, author):
    """Создаем 10 объектов комментариев к одной новости."""
    now = timezone.now()
    comments = []
    for index in range(10):
        comment = Comment(
            news=news,
            author=author,
            text=f'Текст {index}',
            created=now + timedelta(days=index)
        )
        comments.append(comment)

    Comment.objects.bulk_create(comments)

    return comments
