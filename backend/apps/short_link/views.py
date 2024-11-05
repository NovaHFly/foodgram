from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request

from .models import ShortLink
from .util import extract_host_with_schema


@api_view(['get'])
@permission_classes([AllowAny])
def unshorten_link(request: Request, short_token: str) -> HttpResponse:
    host_with_schema = extract_host_with_schema(request.get_raw_uri())
    resource_path = get_object_or_404(
        ShortLink,
        short_token=short_token,
    ).full_path
    full_url = f'{host_with_schema}/{resource_path}'
    return HttpResponseRedirect(full_url)
