from django.urls import reverse
from django.conf import settings
from http import HTTPStatus

import pytest

from news.models import News
from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, many_news):
    """Количество новостей на главной странице — не более 10."""
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    object_list = response.context.get('object_list', [])
    news_count = object_list.count()
    assert news_count == min(len(many_news), settings.NEWS_COUNT_ON_HOME_PAGE)
    all_news_count = News.objects.count()
    assert all_news_count == settings.NEWS_COUNT_ON_HOME_PAGE + 1


@pytest.mark.django_db
def test_news_order(client, many_news):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    response = client.get('news:home')
    object_list = response.context.get('object_list', [])
    all_dates = [many_news.date for many_news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, comments):
    """
    Комментарии на странице отдельной новости отсортированы в хронологическом
    порядке: старые в начале списка, новые — в конце.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comments.created for comments in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_author_has_form(author_client, news, comment):
    """
    Авторизованному доступна форма для отправки комментария
    на странице отдельной новости.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news, comment):
    """
    Анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости, а авторизованному доступна.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)

    assert 'form' not in response.context
