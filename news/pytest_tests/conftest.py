import pytest
from django.test.client import Client
from news.models import News, Comment
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости 1',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Текст комментария 1',
        news=news,
        author=author,
    )
    return comment


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }


@pytest.fixture
def many_news():
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
