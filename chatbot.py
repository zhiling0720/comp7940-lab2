from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackContext)
from ChatGPT_HKBU import HKBU_ChatGPT  # 导入你的 ChatGPT 类
import configparser
import logging
import redis

global redis1
global chatgpt

def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    print(config['TELEGRAM']['ACCESS_TOKEN'])

    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']),
                         password=(config['REDIS']['PASSWORD']),
                         port=(config['REDIS']['REDISPORT']),
                         decode_responses=(config['REDIS']['DECODE_RESPONSE']),
                         username=(config['REDIS']['USER_NAME']))

    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s -%(message)s',
                        level=logging.INFO)

    # Register a dispatcher to handle message
    # Disable echo handler since we are using ChatGPT now
    # echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    # dispatcher.add_handler(echo_handler)

    # Register the dispatcher for ChatGPT
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)  # 创建一个 ChatGPT 实例
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    # Register other command handlers
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello_command))
    print("Starting the bot...")
    updater.start_polling(timeout=600)
    print("Bot started polling...")
    updater.idle()

def equiped_chatgpt(update, context):
    """ChatGPT function that replies to the user's input."""
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)  # 使用 ChatGPT 的 submit 方法
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

def echo(update, context):
    """Echo function (currently not used)."""
    reply_message = update.message.text.upper()
    logging.info("Update:" + str(update))
    logging.info("context:" + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def hello_command(update: Update, context: CallbackContext) -> None:
    """Send a greeting when the command /hello is issued."""
    # Check if the user provided a name
    if not context.args:
        update.message.reply_text("Usage: /hello <name>")
        return
    # Extract the name from the command arguments
    name = " ".join(context.args)
    # Reply with the greeting
    update.message.reply_text(f'Good day, {name}!')

def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]  # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg + ' for ' + redis1.get(msg) + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

if __name__ == '__main__':
    main()
