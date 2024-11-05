from django.contrib import admin

from .models import UserSubscriptions


@admin.register(UserSubscriptions)
class UserSubscriptionsAdmin(admin.ModelAdmin):
    list_display = ['user']
    list_display_links = ['user']
    filter_horizontal = ['users']
