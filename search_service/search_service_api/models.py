from django.db import models
from django.contrib.auth.models import User, Permission


class PermissionUser(models.Model):
    permission_to_view = models.BooleanField(default=False)
    permission_to_view_and_delete = models.BooleanField(default=False)
    user = models.OneToOneField(User, related_name='permissions', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):

        permission_to_view = Permission.objects.get(
            codename='view_searcharea'
        )
        permission_to_delete = Permission.objects.get(
            codename='delete_searcharea'
        )
        self.user.user_permissions.clear()

        if self.permission_to_view:
            self.user.user_permissions.add(permission_to_view)

        if self.permission_to_view_and_delete:
            self.user.user_permissions.add(permission_to_view, permission_to_delete)

        super(PermissionUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.__str__()


class BotUser(models.Model):
    user_id = models.IntegerField(verbose_name='Идентификатор пользователя telegram', primary_key=True)
    username = models.CharField(verbose_name='Юзернейм пользователя', max_length=255, blank=True, null=True)

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
