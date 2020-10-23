from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import BotUser, ResultSearch, SearchArea, PermissionUser


class ResultsInline(admin.TabularInline):
    model = ResultSearch


class PermissionUserInlines(admin.TabularInline):
    model = PermissionUser


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username')
    inlines = [ResultsInline, ]


admin.site.register(PermissionUser)
admin.site.register(ResultSearch)
admin.site.register(SearchArea)
