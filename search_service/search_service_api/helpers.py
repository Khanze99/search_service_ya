from django.core.exceptions import ObjectDoesNotExist

from .models import ResultSearch, BotUser


def get_history(user):
    """
    :param user: telegram.user.User
    :return: result: dict: result: list, count: int
    """
    bot_user = BotUser.objects.get(user_id=user.id)
    count = bot_user.results.all().count()
    objects_list = bot_user.results.all().values('query', 'result', 'query_date')[:5]
    result = {'result': objects_list, 'count': count}

    return result


def check_user_in_db(user):
    """

    :param user: telegram.user.User
    :return: flag: boolean
    """
    try:
        user = BotUser.objects.get(user_id=user.id)
        have_a_user_in_db = True
    except ObjectDoesNotExist:
        have_a_user_in_db = False

    return have_a_user_in_db
