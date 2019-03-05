#!/usr/bin/env python
import logging
import sys
import requests


from telegram.ext import Updater, CommandHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
URL = "https://publico.elterrat.com/programa/la-resistencia/formulario/"
HEADERS = {"User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}


def get_value(line):
    return line.replace(" ", "").split("=")[1].replace("[","").replace("]","").replace('"','').rstrip(";").split(",")


def checker(context):
    response = requests.request("GET", url=URL, headers=HEADERS).text
    #logger.info("checking")
    #contents = open("prueba.txt", "r").read()
    lines = response.splitlines()
    for index in range(len(lines)):
        if "if (fechas) {" in lines[index]:
            days_vars = lines[index+1].replace(" ", "").split("=")
            days_off_var = days_vars[0]
            days_var = days_vars[1].rstrip(".")
            break

    days_offs = dict()
    for index in range(len(lines)):
        if "var " + days_off_var in lines[index]:
            days_offs[days_off_var] = get_value(lines[index])
            if len(days_offs) >= 2:
                break

        elif "var " + days_var in lines[index]:
            days_offs[days_var] = get_value(lines[index])
            if len(days_offs) >= 2:
                break

    days_off = days_offs[days_off_var]
    days_all = days_offs[days_var]

    if len(days_all) != len(days_off):
        logger.info("Puede que haya fechas disponibles")
        send_message(context, "Puede que haya fechas disponibles")
        for day in days_all:
            if day not in days_off:
                logger.info('Fecha disponible "%s"', day)
                send_message(context, "fecha disponible " + day)

   

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    update.message.reply_text('Holi! usa /set <minutos> para ver si puedes ver al pachacho')


def send_message(context, message):
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text=message)


def set_timer(update, context):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        interval = int(context.args[0]) * 60
        if interval < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        
        # Add job to queue
        #job = context.job_queue.run_once(alarm, due, context=chat_id)
        job = context.job_queue.run_repeating(checker, interval, first=0, context=chat_id)
        context.chat_data['job'] = job

        update.message.reply_text('Esta todo bien puesto')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <minutes>')


def unset(update, context):
    """Remove the job if the user changed their mind."""
    if 'job' not in context.chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = context.chat_data['job']
    job.schedule_removal()
    del context.chat_data['job']

    update.message.reply_text('Timer successfully unset!')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    token = sys.argv[1]

    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()