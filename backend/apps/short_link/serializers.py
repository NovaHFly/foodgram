from rest_framework import serializers

from common.util import generate_token

from .models import ShortLink
from .util import extract_host_with_schema


class ShortLinkSerializer(serializers.ModelSerializer):
    full_path = serializers.CharField()

    class Meta:
        model = ShortLink
        fields = ['id', 'full_path']

    def to_representation(self, short_link: ShortLink) -> dict[str, str]:
        url = self.context['request'].get_raw_uri()
        host_with_schema = extract_host_with_schema(url)
        return {
            'short-link': f'{host_with_schema}/s/{short_link.short_token}/'
        }

    def create(self, validated_data: dict) -> ShortLink:
        full_path = validated_data.pop('full_path')

        if ShortLink.objects.filter(full_path=full_path).exists():
            return ShortLink.objects.get(full_path=full_path)

        while True:
            short_token = generate_token()
            if not ShortLink.objects.filter(short_token=short_token).exists():
                break

        short_link = ShortLink.objects.create(
            full_path=full_path,
            short_token=short_token,
        )

        return short_link
