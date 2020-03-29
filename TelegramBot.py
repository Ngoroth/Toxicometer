import logging

from telegram import Update, User, InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence, \
    InlineQueryHandler
from uuid import uuid4

import SentimentAnalyzer
from Models import UserToxicityData

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Привет! Я - Токсикометр и я буду замерять токсичность вашего чата.")


def analyse(update: Update, context: CallbackContext):
    user_chat_toxicity_data = UserToxicityData()
    user_global_bot_toxicity_data = UserToxicityData()

    if __get_user_key(update.message.from_user) in context.chat_data:
        user_chat_toxicity_data = context.chat_data[__get_user_key(update.message.from_user)]
    if __get_user_key(update.message.from_user) in context.bot_data:
        user_global_bot_toxicity_data = context.chat_data[__get_user_key(update.message.from_user)]

    user_chat_toxicity_data.messages_count += 1
    user_chat_toxicity_data.total_toxicity += SentimentAnalyzer.get_toxicity(update.message.text)

    user_global_bot_toxicity_data.messages_count += 1
    user_global_bot_toxicity_data.total_toxicity += SentimentAnalyzer.get_toxicity(update.message.text)

    context.chat_data[__get_user_key(update.message.from_user)] = user_chat_toxicity_data
    context.bot_data[__get_user_key(update.message.from_user)] = user_global_bot_toxicity_data


def get_top_toxics(update: Update, context: CallbackContext):
    text = 'Самые токсичные здесь: \n'
    for i in sorted(context.chat_data.items(), key=lambda ud: ud[1].get_toxic_coefficient())[-3:]:
        text += i[0] + ' {0}\n'.format(i[1].get_toxic_coefficient())
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)


def my_toxicity(update: Update, context: CallbackContext):
    user_key = __get_user_key(update.message.from_user)
    if user_key not in context.bot_data:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Общий коэффициент токсичности {0} еще не рассчитан'.format(user_key))
        return
    toxicity_data = context.bot_data[user_key]
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Общий коэффициент токсичности {0} равен {1}'.format(user_key,
                                                                                       toxicity_data.get_toxic_coefficient()))


def my_toxicity_here(update: Update, context: CallbackContext):
    user_key = __get_user_key(update.message.from_user)
    if update.message.from_user.username not in context.chat_data:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Коэффициент токсичности {0} в этом чате еще не рассчитан'.format(user_key))
        return
    toxicity_data = context.chat_data[user_key]
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Коэффициент токсичности {0} в этом чате равен {1}'
                             .format(user_key, toxicity_data.get_toxic_coefficient()))


def lookToxicity(update: Update, context: CallbackContext):
    """Handle the inline query."""
    query = update.inline_query.query
    if query not in context.bot_data:
        update.inline_query.answer([])
        return

    toxicity_data: UserToxicityData = context.bot_data[query]
    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title='Токсичность {0} равна {1}'.format(query, toxicity_data.get_toxic_coefficient()),
            input_message_content=InputTextMessageContent(
                'Токсичность {0} равна {1}, учтено {2} сообщений'.format(query, toxicity_data.get_toxic_coefficient(),
                                                                         toxicity_data.messages_count)))]

    update.inline_query.answer(results)


def __get_user_key(user: User) -> str:
    if user.username is not None:
        return user.username
    else:
        return user.first_name + ' ' + (user.last_name or '')


def main():
    persistence = PicklePersistence(filename='db')
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
    analyse_handler = MessageHandler(Filters.text, analyse)
    dispatcher.add_handler(analyse_handler)
    dispatcher.add_handler(InlineQueryHandler(lookToxicity))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
