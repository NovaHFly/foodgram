from django.apps import AppConfig


class FavoritesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'favorites'
    verbose_name = 'Избранное'

    def ready(self) -> None:
        # Need these imports to execute code inside
        from . import filters, serializers  # noqa: F401
