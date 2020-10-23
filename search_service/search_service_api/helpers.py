import logging

from django.core.exceptions import ObjectDoesNotExist

from .models import ResultSearch, BotUser, SearchArea

logger = logging.getLogger('service')


def get_history(user):
    """
    :param user: telegram.user.User
    :return: result: dict: result: list, count: int
    """
    logger.info('Get history from db')
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

    logger.info('Check user {} in db'.format(user.username))
    try:
        BotUser.objects.get(user_id=user.id)
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


def get_area_use_dict():
    area_use_dict = {}
    for area in SearchArea.objects.values('name'):
        area_use_dict[area['name']] = False

    return area_use_dict


def set_area_use_flag(area_dict, description_list):
    for area in area_dict:
        if area in description_list:
            area_dict[area] = True

    return area_dict


def get_allowed_addresses(result_geocode):
    """

    :param result_geocode: dict
    :return: list
    """
    area_use_dict = get_area_use_dict()
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
            logger.error(f'KEY ERROR : {feature}')
            continue

        if address is not None:
            filtered_objects = SearchArea.objects.filter(name__in=description_list)

        for area in area_use_dict:
            if area in description_list:
                if area_use_dict[area]:
                    continue

                if filtered_objects:
                    area_use_dict[area] = True
                    allowed_addresses_list.append(address)

    return allowed_addresses_list


def save_result(bot_user_id, query, result):
    """

    :param bot_user_id: int
    :param query: str
    :param result: str
    :return: bool
    """
    logger.info('Save result query')
    ResultSearch.objects.create(bot_user_id=bot_user_id, query=query, result=result)
