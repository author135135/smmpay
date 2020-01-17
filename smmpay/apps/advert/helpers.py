import os

from time import time
from datetime import datetime
from hashlib import sha1
from urllib.parse import urlparse

from django.utils.deconstruct import deconstructible


@deconstructible
class RenameFile(object):
    def __init__(self, path, *args, **kwargs):
        self.path = path

    def __call__(self, instance, filename):
        # Fix for filenames with query params
        filename = urlparse(filename).path

        try:
            name, extension = filename.rsplit('.', 1)
        except ValueError:
            name, extension = filename, None

        name = name.encode('utf-8')

        if instance.pk:
            salt = (str(instance.pk) + str(time())).encode('utf-8')
        else:
            salt = str(time()).encode('utf-8')

        if extension is not None:
            filename = '{0}.{1}'.format(sha1(name + salt).hexdigest()[::2], extension)
        else:
            filename = sha1(name + salt).hexdigest()[::2]

        return os.path.join(datetime.now().strftime(self.path), filename)
