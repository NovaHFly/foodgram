from django.urls import include, path

from recipes.views import unshorten_link

urlpatterns = [
    path('api/', include('recipes.urls')),
    path('api/', include('subscriptions.urls')),
    path('api/', include('users.urls')),
    path('s/<str:short_url>/', unshorten_link, name='unshorten_link'),
]
