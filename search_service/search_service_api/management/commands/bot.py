import logging
import requests

from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import KeyboardButton, ReplyKeyboardMarkup

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from search_service_api.helpers import get_history, check_user_in_db, \
    get_allowed_addresses, save_result
from search_service_api.models import BotUser

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('service')


class Command(BaseCommand):
    # stages
    CHOICE, DATA, CREATE = range(3)

    def start(self, update, context):
        user = update.message.from_user
        logger.info("User %s started the conversation.", user.first_name)
        text = 'Добро пожаловать! Я бот, который преобразует ваш короткий запрос через API геокодер Яндекса в полный адрес с фильтрацией разрешенных областей\n' \
               'QR клавиатура:\n' \
               '1. "Новый запрос" - новый запрос на геокодирование места\n' \
               '2. "История" - показывает 5 ваших последних запросов\n' \
               '3. "Завершение" - завершение процесса, чтобы возобновить вызовите команду /start\n' \
               '\n' \
               'Чтобы вернуться в изначальное состояние отправьте комманду /start'

        keyboard = [
            [
                KeyboardButton('Новый поиск 🌏'),
                KeyboardButton('История 💾'),
                KeyboardButton('Завершить')
            ]
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text(text, reply_markup=reply_markup)

        return self.CHOICE

    def callback_new_query(self, update, context):
        user = update.message.from_user
        flag = check_user_in_db(user)

        logger.info('Checking user {} in the database'.format(user.first_name))

        if flag is False:
            keyboard = [
                [
                    KeyboardButton('Да'),
                    KeyboardButton('Нет')
                ]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            update.message.reply_text(text='Для того чтобы пользоваться функционалом, нужно чтобы вы подтвердили'
                                           ' использование ваших данных - id и username',
                                      reply_markup=reply_markup)
            return self.CREATE

        update.message.reply_text(
            'Введите запрос для поиска или команду /skip если хотите отменить запрос на геокодирование:')
        return self.DATA

    def skip(self, update, context):
        user = update.message.from_user
        text = 'Вы отменили запрос.'
        logger.info('Сanceling the request to save the user {} in the database'.format(user.first_name))
        keyboard = [
            [
                KeyboardButton('Новый поиск 🌏'),
                KeyboardButton('История 💾'),
                KeyboardButton('Завершить')
            ]
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text(text, reply_markup=reply_markup)

        return self.CHOICE

    def callback_message_new_query(self, update, context):
        user = update.message.from_user
        user_id = user.id
        query = update.message.text
        logger.info('User {user} request for geocoding: {query}'.format(user=user.first_name, query=query))
        params = {'geocode': query,
                  'apikey': settings.YANDEX_GEOCODER_TOKEN,
                  'format': 'json'}
        result = requests.get(settings.YANDEX_URL, params=params).json()
        allowed_addresses = get_allowed_addresses(result)

        if allowed_addresses:
            text = allowed_addresses[0]
        else:
            text = 'Не найдено'

        save_result(user_id, query, text)
        keyboard = [
            [
                KeyboardButton('Новый поиск 🌏'),
                KeyboardButton('История 💾'),
                KeyboardButton('Завершить')
            ]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text(text=text, reply_markup=reply_markup)

        return self.CHOICE

    def callback_history(self, update, context):

        user = update.message.from_user
        flag = check_user_in_db(user)
        logger.info('Retrieving user {} history'.format(user.first_name))

        if flag is False:
            keyboard = [
                [
                    KeyboardButton('Да'),
                    KeyboardButton('Нет')
                ]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            update.message.reply_text(text='Для того чтобы пользоваться функционалом, нужно чтобы вы подтвердили'
                                           ' использование ваших данных - id и username',
                                      reply_markup=reply_markup)
            return self.CREATE

        result = get_history(user)
        count = result['count']
        results_list = result['result']
        text = 'Вы совершили {count} поисковых запросов\n'.format(count=count)

        for res in results_list:
            text += '{query} -> {result} ({date})\n'.format(query=res['query'],
                                                            result=res['result'],
                                                            date=res['query_date'].strftime('%d.%m.%y'))

        keyboard = [
            [
                KeyboardButton('Новый поиск 🌏'),
                KeyboardButton('История 💾'),
                KeyboardButton('Завершить')
            ]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text(text=text, reply_markup=reply_markup)

        return self.CHOICE

    def callback_create_user(self, update, context):
        user = update.message.from_user
        logger.info('Create new user {}'.format(user.first_name))
        try:
            BotUser.objects.create(user_id=user.id, username=user.username)
        except:
            BotUser.objects.create(user_id=user.id)

        keyboard = [
            [
                KeyboardButton('Новый поиск 🌏'),
                KeyboardButton('История 💾'),
                KeyboardButton('Завершить')
            ]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text(text='Пользователь создан. Выберите следующие действия на клавиатуре', reply_markup=reply_markup)

        return self.CHOICE

    def skip_create_user(self, update, context):
        user = update.message.from_user
        logger.info('User {} skipping'.format(user.first_name))
        update.message.reply_text(text='Вы отказались. Для того чтобы перейти в начальное состояние используйте /start')
        return ConversationHandler.END

    def end_process(self, update, context):
        user = update.message.from_user
        logger.info('End of work | {}'.format(user.first_name))
        update.message.reply_text(text='Вы завершили процесс работы с ботом. Для того чтобы возобновить работу, напишите команду /start')
        return ConversationHandler.END

    def main(self):
        updater = Updater(token=settings.TELEGRAM_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                self.CHOICE: [
                    MessageHandler(Filters.regex('Новый поиск'), self.callback_new_query),
                    MessageHandler(Filters.regex('История'), self.callback_history),
                    MessageHandler(Filters.regex('Завершить'), self.end_process)
                ],
                self.DATA: [
                    MessageHandler(Filters.text & (~Filters.command), self.callback_message_new_query),
                    CommandHandler('skip', self.skip)
                ],
                self.CREATE: [
                    MessageHandler(Filters.regex('^Да$'), self.callback_create_user),
                    MessageHandler(Filters.regex('^Нет$'), self.skip_create_user)
                ]
            },
            fallbacks=[CommandHandler('start', self.start)]
        )

        dispatcher.add_handler(conv_handler)
        updater.start_polling()

        updater.idle()

    def handle(self, *args, **options):
        self.main()
