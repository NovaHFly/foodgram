from django.contrib import admin

from users.admin import UserAdmin

from .models import UserSubscriptions


class UserSubscriptionsInline(admin.StackedInline):
    model = UserSubscriptions
    filter_horizontal = ['users']


@admin.register(UserSubscriptions)
class UserSubscriptionsAdmin(admin.ModelAdmin):
    list_display = ['user']
    list_display_links = ['user']
    filter_horizontal = ['users']


UserAdmin.inlines += [UserSubscriptionsInline]
