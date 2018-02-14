import pytest

from smmpay.apps.blog.models import Post


def test_is_app_installed(settings):
    assert 'smmpay.apps.blog' in settings.INSTALLED_APPS


@pytest.mark.django_db
@pytest.mark.usefixtures('setup_default_data')
class TestPost(object):
    def test_item_count(self):
        assert Post.objects.count() == 5

    def test_published_objects_manager(self):
        filtered_objects_count = Post.objects.filter(status=Post.PUBLISHED).count()
        managed_objects_count = Post.published_objects.count()

        assert filtered_objects_count == managed_objects_count

    def test_object_repr(self):
        post = Post.objects.first()

        assert post.title == str(post)

    def test_db_table_name(self):
        assert Post._meta.db_table == 'blog_post'
