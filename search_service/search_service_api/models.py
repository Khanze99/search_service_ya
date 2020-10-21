from django.db import models
from django.utils import timezone


class BotUser(models.Model):
    user_id = models.IntegerField(verbose_name='Идентификатор пользователя', unique=True)
    username = models.CharField(verbose_name='Никнейм пользователя', max_length=255, blank=True, null=True)

    def __str__(self):
        if self.username:
            return 'Username: {} ID: {}'.format(self.username, self.user_id)

        return str(self.user_id)


class ResultSearch(models.Model):
    query = models.CharField(verbose_name='Запрос', max_length=255)
    result = models.TextField(verbose_name='Результат запроса')
    query_date = models.DateTimeField(verbose_name='Дата запроса', auto_now_add=True)
    bot_user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name='results')

    def __str__(self):
        return self.query


class SearchArea(models.Model):
    name = models.TextField(verbose_name='Область', null=True, blank=True)

    def __str__(self):
        return self.name
