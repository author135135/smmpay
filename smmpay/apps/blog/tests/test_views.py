import pytest

from django.core.urlresolvers import reverse
from smmpay.apps.blog.models import Post


def test_is_app_installed(settings):
    assert 'smmpay.apps.blog' in settings.INSTALLED_APPS


@pytest.mark.django_db
@pytest.mark.usefixtures('setup_default_data')
class TestIndexView(object):
    def test_page_response_status_code(self, client):
        response = client.get(reverse('blog:index'))

        assert response.status_code == 200

    def test_page_context(self, client):
        response = client.get(reverse('blog:index'))

        assert 'posts' in response.context

    def test_posts_statuses(self, client):
        response = client.get(reverse('blog:index'))
        posts = response.context['posts']

        assert all([post.status == Post.PUBLISHED for post in posts])


@pytest.mark.django_db
@pytest.mark.usefixtures('setup_default_data')
class TestPostView(object):
    def test_enabled_post_page_response_status_code(self, client):
        post = Post.published_objects.first()
        response = client.get(post.get_absolute_url())

        assert response.status_code == 200

    def test_disabled_post_page_response_status_code(self, client):
        post = Post.objects.filter(status=Post.DRAFT).first()
        response = client.get(post.get_absolute_url())

        assert response.status_code == 404
