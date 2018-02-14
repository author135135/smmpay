import os
import pytest
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smmpay.settings')


def pytest_configure():
    django.setup()


@pytest.fixture(scope='session')
def django_db_modify_db_settings():
    from django.conf import settings

    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }


@pytest.fixture
def setup_default_data():
    from smmpay.apps.blog.models import Post

    Post.objects.bulk_create([
        Post(title='Post title 1', url='post-1', content='Post number one', image=None, status=Post.PUBLISHED),
        Post(title='Post title 2', url='post-2', content='Post number two', image=None, status=Post.PUBLISHED),
        Post(title='Post title 3', url='post-3', content='Post number three', image=None, status=Post.DRAFT),
        Post(title='Post title 4', url='post-4', content='Post number four', image=None, status=Post.DRAFT),
        Post(title='Post title 5', url='post-5', content='Post number five', image=None, status=Post.DRAFT)
    ])
