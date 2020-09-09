import json
import logging
import os
from flask import Flask, request
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher
from telegram import Update, Bot, ReplyKeyboardMarkup
from utils import get_reply, fetch_news, topics_keyboard
#updater recives the update from the telegram and report back into the dispatcher

# enable logging to handle any time of error during the running time of the bot
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "1391633156:AAFgrUTDuvOm7cEt1Gr3tUhbfdqdwyKGPh4"

# creating a app from flask
app = Flask(__name__)

#creating out first route
@app.route('/')
def index():
    return "Hello!"

@app.route(f'/{TOKEN}', methods=['GET','POST'])
def webhook():
    # webhook view which receives updates from telegram
    #create update object from json-format request data
    # telegram continously send you the updates in json format so we catch this json format update and convert it into standard update object of telegram bot
    update = Update.de_json(request.get_json(), bot)
    #process update
    dp.process_update(update)
    return "ok"

def start(bot,update):
    print(update)
    author = update.message.from_user.first_name
    reply = "Hi! {}".format(author)
    bot.send_message(chat_id=update.message.chat_id, text=reply)


def _help(bot, update):
    help_text = "Hi! How can we help you ?"
    bot.send_message(chat_id=update.message.chat_id, text=help_text)

def reply_text(bot, update):
    intent, reply = get_reply(update.message.text, update.message.chat_id)
    if intent == "get_news":
        articles = fetch_news(reply)
        for article in articles:
            bot.send_message(chat_id=update.message.chat_id, text=article['link'])
    else:
        bot.send_message(chat_id=update.message.chat_id, text=reply)

def echo_sticker(bot, update):
    bot.send_sticker(chat_id=update.message.chat_id, sticker=update.message.sticker.file_id)

def error(bot, update):
    logger.error("Update '%s' casused error '%s'",update,update.error)

def news(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Choose a Category", reply_markup=ReplyKeyboardMarkup(keyboard=topics_keyboard,one_time_keyboard=True))


bot = Bot(TOKEN)
dp = Dispatcher(bot,None)
try:
# as we are using ngrok on port 8443 we have to run our flash server at the same in order to deploy it online
    bot.set_webhook("https://dry-harbor-99846.herokuapp.com/" + TOKEN)
except Exception as e:
    print(e)

    # this dispatcher function take two parameter first one is bot and second one is queue to handle update requests in it, but here we are not using any kind of multithreaded bot so we can pass it as None and rest is on bot
dp.add_handler(CommandHandler("start",start))
dp.add_handler(CommandHandler("help",_help))
dp.add_handler(CommandHandler("news",news))
dp.add_handler(MessageHandler(Filters.text, reply_text))
dp.add_handler(MessageHandler(Filters.sticker, echo_sticker))
dp.add_error_handler(error)

if __name__ == "__main__":
    # app.run(port=8443)

    app.run(host="0.0.0.0", port=int(os.environ.get('PORT',5000)))