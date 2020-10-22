import logging

from django.core.exceptions import ObjectDoesNotExist

from .models import ResultSearch, BotUser, SearchArea


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


def edit_strip_obj_in_list(objects: list):
    """

    :param objects: list
    :return:
    """
    edited_list = []
    for i in range(len(objects)):
        edited_obj = objects[i].strip()
        edited_list.append(edited_obj)

    return edited_list


def get_allowed_addresses(result_geocode):
    """

    :param result_geocode: dict
    :return:
    """
    features = result_geocode['response']['GeoObjectCollection']['featureMember']
    allowed_addresses_list = []
    address = None
    description_list = []
    filtered_objects = []

    for feature in features:
        try:
            address = feature['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
            description_list = edit_strip_obj_in_list(feature['GeoObject']['description'].split(','))
        except KeyError:
            print(f'KEY ERROR : {feature}')

        if address is not None:
            filtered_objects = SearchArea.objects.filter(name__in=description_list)

        if filtered_objects:
            allowed_addresses_list.append(address)

    return allowed_addresses_list


def save_result(bot_user_id, query, result):
    """

    :param bot_user_id: int
    :param query: str
    :param result: str
    :return: bool
    """
    ResultSearch.objects.create(bot_user_id=bot_user_id, query=query, result=result)
