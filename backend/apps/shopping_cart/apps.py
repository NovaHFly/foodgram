from django.apps import AppConfig


class ShoppingCartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shopping_cart'
    verbose_name = 'Корзина покупок'

    def ready(self) -> None:
        # Need these imports to execute code inside modules
        from . import filters, serializers  # noqa: F401
