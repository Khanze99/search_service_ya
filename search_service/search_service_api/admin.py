from django.contrib import admin
from django.contrib.auth.models import User

from .models import BotUser, ResultSearch, SearchArea, CustomerUser


admin.site.unregister(User)
admin.site.register(CustomerUser)


class ResultsInline(admin.TabularInline):
    model = ResultSearch


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username')
    inlines = [ResultsInline, ]


admin.site.register(ResultSearch)
admin.site.register(SearchArea)
