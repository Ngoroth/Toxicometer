import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict

from telegram import Update, User, InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence, \
    InlineQueryHandler
from uuid import uuid4

import SentimentAnalyzer
from Models import ToxicityData

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
bot_info: Dict[str, int] = {'command_completed': 0}
chat_key = 'c77dcd1a-6139-4adc-ad67-698d57b9e1c6'


def bot_information(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Выполнено {0} команд'.format(bot_info['command_completed']))


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Привет! Я - Токсикометр и я буду замерять токсичность вашего чата.")
    bot_info['command_completed'] += 1


def analyse(update: Update, context: CallbackContext):
    __update_toxicity_data(context.chat_data, __get_user_key(update.message.from_user), update.message.text)
    __update_toxicity_data(context.bot_data, __get_user_key(update.message.from_user), update.message.text)
    __update_toxicity_data(context.chat_data, chat_key, update.message.text)


def __update_toxicity_data(data_storage: defaultdict, key: str, message_text: str):
    toxicity_data = ToxicityData()

    if key in data_storage:
        toxicity_data = data_storage[key]

    toxicity_data.messages_count += 1
    toxicity_data.total_sentiment_data += SentimentAnalyzer.get_sentiment(message_text)
    toxicity_data.changed_at = datetime.now()

    data_storage[key] = toxicity_data


def get_top_toxics(update: Update, context: CallbackContext):
    text = 'Самые токсичные здесь: \n'

    count: int = 0
    for i in sorted(context.chat_data.items(), key=lambda ud: ud[1].get_toxicity(), reverse=True):
        if i[0] == chat_key:
            continue
        text += '🤮 ' + i[0] + ' {0}\n'.format(i[1].get_toxicity())
        count += 1
        if count == 3:
            break

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)
    bot_info['command_completed'] += 1


def my_toxicity(update: Update, context: CallbackContext):
    send_toxicity(update, context, context.bot_data, '(глобальные данные)')


def my_toxicity_here(update: Update, context: CallbackContext):
    send_toxicity(update, context, context.chat_data, '(данные этого чата)')


def send_toxicity(update: Update, context: CallbackContext, data_storage: defaultdict, title: str):
    user_key = __get_user_key(update.message.from_user)
    if user_key not in data_storage:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Коэффициент токсичности {0} в этом чате еще не рассчитан'.format(user_key))
        return
    toxicity_data: ToxicityData = data_storage[user_key]
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='<b>{0}</b> {1}\r\n'
                                  '🤢 <u>Токсичность:</u> {2}\r\n'
                                  '☹ Негативность: {3}\r\n'
                                  '😐 Нейтральность: {4}\r\n'
                                  '😃 Позитивность: {5}\r\n'
                                  '🧐 Иное: {6}'
                             .format(user_key,
                                     title,
                                     toxicity_data.get_toxicity(),
                                     toxicity_data.get_sentiment_data_coefficients().negative,
                                     toxicity_data.get_sentiment_data_coefficients().neutral,
                                     toxicity_data.get_sentiment_data_coefficients().positive,
                                     toxicity_data.get_sentiment_data_coefficients().other),
                             parse_mode=ParseMode.HTML)
    bot_info['command_completed'] += 1


def look_toxicity(update: Update, context: CallbackContext):
    query = update.inline_query.query
    if query not in context.bot_data:
        update.inline_query.answer([])
        return

    toxicity_data: ToxicityData = context.bot_data[query]
    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title='Токсичность {0} равна {1}'.format(query, toxicity_data.get_toxicity()),
            input_message_content=InputTextMessageContent(
                'Токсичность {0} равна {1}, учтено {2} сообщений'.format(query, toxicity_data.get_toxicity(),
                                                                         toxicity_data.messages_count)))]

    update.inline_query.answer(results)


def chat_mood(update: Update, context: CallbackContext):
    if chat_key not in context.chat_data:
        context.chat_data[chat_key] = ToxicityData()

    toxicity_data: ToxicityData = context.chat_data[chat_key]

    if toxicity_data.changed_at < datetime.now() - timedelta(hours=2):
        toxicity_data = ToxicityData()
        context.chat_data[chat_key] = toxicity_data

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=toxicity_data.get_main_sentiment())
    bot_info['command_completed'] += 1


def __get_user_key(user: User) -> str:
    if user.username is not None:
        return user.username
    else:
        return user.first_name + ' ' + (user.last_name or '')


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    persistence = PicklePersistence(filename='Data/db')
    updater = Updater(token='TOKEN', persistence=persistence, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    toxic_top_handler = CommandHandler('toxic_top', get_top_toxics)
    dispatcher.add_handler(toxic_top_handler)
    my_toxicity_handler = CommandHandler('my_toxicity', my_toxicity)
    dispatcher.add_handler(my_toxicity_handler)
    my_toxicity_here_handler = CommandHandler('my_toxicity_here', my_toxicity_here)
    dispatcher.add_handler(my_toxicity_here_handler)
    dispatcher.add_handler(CommandHandler('bot_information', bot_information))
    dispatcher.add_handler(CommandHandler('chat_mood', chat_mood))

    analyse_handler = MessageHandler(Filters.text, analyse)
    dispatcher.add_handler(analyse_handler)
    dispatcher.add_handler(InlineQueryHandler(look_toxicity))

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
