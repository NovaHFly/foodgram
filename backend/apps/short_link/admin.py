from django.contrib import admin

from .models import ShortLink


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ['short_token', 'full_path']
    list_display_links = ['short_token']
