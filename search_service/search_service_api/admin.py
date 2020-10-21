from django.contrib import admin

from .models import BotUser, ResultSearch, SearchArea


class ResultsInline(admin.TabularInline):
    model = ResultSearch


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'username')
    inlines = [ResultsInline, ]


admin.site.register(ResultSearch)
admin.site.register(SearchArea)
