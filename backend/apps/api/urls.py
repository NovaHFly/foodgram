from django.urls import include, path

urlpatterns = [
    path('api/', include('favorites.urls')),
    path('api/', include('recipes.urls')),
    path('api/', include('subscriptions.urls')),
    path('api/', include('users.urls')),
    path('', include('short_link.urls')),
]
