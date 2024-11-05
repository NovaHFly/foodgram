from django.urls import path

from .views import unshorten_link

urlpatterns = [
    path(
        's/<str:short_token>/',
        unshorten_link,
        name='unshorten_link',
    ),
]
