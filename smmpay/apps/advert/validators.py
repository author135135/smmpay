import magic

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _


@deconstructible
class FileMimeTypeValidator(object):
    message = _('Unsupported file type')
    code = 'unsupported_file_type'

    def __init__(self, mime_types, message=None, code=None):
        self.mime_types = mime_types

        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        value.file.seek(0)
        file_mime_type = magic.from_buffer(value.file.read(2048), mime=True)

        if self.mime_types is not None and file_mime_type not in self.mime_types:
            raise ValidationError(self.message, code=self.code)


def get_available_image_extensions():
    try:
        from PIL import Image
    except ImportError:
        return []
    else:
        Image.init()
        return list(Image.MIME.values())


validate_image_file_mime_type = FileMimeTypeValidator(mime_types=get_available_image_extensions())
