import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence

import SentimentAnalyzer
from Models import UserToxicityData

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Привет! Я - Токсикометр замерять токсичность вашего чата.")


def analyse(update: Update, context: CallbackContext):
    toxicity_data = UserToxicityData()

    if "toxicity" in context.user_data:
        toxicity_data = context.user_data["toxicity"]

    toxicity_data.messages_count += 1
    toxicity_data.total_toxicity += SentimentAnalyzer.get_sentiment(update.message.text).negative

    context.user_data["toxicity"] = toxicity_data
    context.chat_data[update.message.from_user.username] = toxicity_data


def get_top_toxics(update: Update, context: CallbackContext):
    text = 'Самые токсичные здесь: \n'
    for i in sorted(context.chat_data.items(), key=lambda ud: ud[1].total_toxicity)[-3:]:
        text += i[0] + ' {0}%\n'.format(i[1].get_toxic_level())
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)


def my_toxicity(update: Update, context: CallbackContext):
    if 'toxicity' not in context.user_data:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='{0} не токсичен'.format(update.message.from_user.username))
        return
    toxicity_data = context.user_data['toxicity']
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='{0} токсичен на {1}%'.format(update.message.from_user.username,
                                                                toxicity_data.get_toxic_level()))


def my_toxicity_here(update: Update, context: CallbackContext):
    if update.message.from_user.username not in context.chat_data:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='{0} не токсичен в этом чате'.format(update.message.from_user.username))
        return
    toxicity_data = context.chat_data[update.message.from_user.username]
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='{0} токсичен в этом чате на {1}%'.format(update.message.from_user.username,
                                                                            toxicity_data.get_toxic_level()))


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
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
