from django.urls import reverse
from pytest_django.asserts import assertRedirects
from http import HTTPStatus

import pytest

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    comments_count_before_post = Comment.objects.count()
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before_post


@pytest.mark.django_db
def test_user_can_create_comment(author_client, news, form_data):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    comments_count_before_post = Comment.objects.count()
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before_post+1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comments_count_before_post = Comment.objects.count()
    response = author_client.post(url, data=bad_words_data)
    form_errors = response.context['form'].errors
    assert 'text' in form_errors
    assert WARNING in form_errors['text'][0]
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before_post


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, form_data, comment, news):
    """
    Авторизованный пользователь может
    редактировать свои комментарии.
    """
    edit_url = reverse('news:edit', args=(comment.id,))
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment = Comment.objects.get(pk=comment.pk)
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, form_data, comment, news):
    """Авторизованный пользователь может удалять свои комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'
    comments_count_before_delete = Comment.objects.count()
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before_delete-1


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        form_data,
        comment,
        news
):
    """
    Авторизованный пользователь не может редактировать
    чужие комментарии.
    """
    edit_url = reverse('news:edit', args=(comment.id,))
    comment_before_post = Comment.objects.get(pk=comment.pk)
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment = Comment.objects.get(pk=comment.pk)
    assert comment.text == comment_before_post.text


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
        not_author_client,
        form_data,
        comment,
        news
):
    """
    Авторизованный пользователь не может
    удалять чужие комментарии.
    """
    delete_url = reverse('news:delete', args=(comment.id,))
    comments_count_before_delete = Comment.objects.count()
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before_delete
