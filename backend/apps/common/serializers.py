import base64

from django.core.files.base import ContentFile
from rest_framework.serializers import ImageField

from .util import generate_token


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(
                base64.b64decode(imgstr),
                name=f'{generate_token(16)}.{ext}',
            )

        return super().to_internal_value(data)
