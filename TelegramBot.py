import logging

from telegram import Update, User
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence

import SentimentAnalyzer
from Models import UserToxicityData

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Привет! Я - Токсикометр и я буду замерять токсичность вашего чата.")


def analyse(update: Update, context: CallbackContext):
    user_global_toxicity_data = UserToxicityData()
    user_chat_toxicity_data = UserToxicityData()

    if "toxicity" in context.user_data:
        user_global_toxicity_data = context.user_data["toxicity"]
    if __get_user_key(update.message.from_user) in context.chat_data:
        user_chat_toxicity_data = context.chat_data[__get_user_key(update.message.from_user)]

    user_global_toxicity_data.messages_count += 1
    user_global_toxicity_data.total_toxicity += SentimentAnalyzer.get_sentiment(update.message.text).negative

    user_chat_toxicity_data.messages_count += 1
    user_chat_toxicity_data.total_toxicity += SentimentAnalyzer.get_sentiment(update.message.text).negative

    context.user_data["toxicity"] = user_global_toxicity_data
    context.chat_data[__get_user_key(update.message.from_user)] = user_chat_toxicity_data


def get_top_toxics(update: Update, context: CallbackContext):
    text = 'Самые токсичные здесь: \n'
    for i in sorted(context.chat_data.items(), key=lambda ud: ud[1].get_toxic_level())[-3:]:
        text += i[0] + ' {0}%\n'.format(i[1].get_toxic_level())
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)


def my_toxicity(update: Update, context: CallbackContext):
    user_key = __get_user_key(update.message.from_user)
    if 'toxicity' not in context.user_data:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='{0} не токсичен'.format(user_key))
        return
    toxicity_data = context.user_data['toxicity']
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='{0} токсичен на {1}%'.format(user_key,
                                                                toxicity_data.get_toxic_level()))


def my_toxicity_here(update: Update, context: CallbackContext):
    user_key = __get_user_key(update.message.from_user)
    if update.message.from_user.username not in context.chat_data:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='{0} не токсичен в этом чате'.format(user_key))
        return
    toxicity_data = context.chat_data[user_key]
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='{0} токсичен в этом чате на {1}%'.format(user_key,
                                                                            toxicity_data.get_toxic_level()))


def __get_user_key(user: User) -> str:
    if user.username is not None:
        return user.username
    else:
        return user.first_name + ' ' + (user.last_name or '')


def main():
    persistence = PicklePersistence(filename='db')
    updater = Updater(token='1052374518:AAFEyQiZwH1U4Sr9OADy04F3n4Pe089r3F0', persistence=persistence, use_context=True)
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
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
