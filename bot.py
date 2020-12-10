import calendar

import telebot

import config
from dbworker import reset_user, get_param, set_param, get_user_info
from dfworker import get_tmpr, get_prcp, get_final, get_results

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=["help"])
def user_reset(message):
    uid = message.chat.id
    bot.send_message(uid, 'Hello! I am a WhereIsWeatherBot.\nI can find places in the world with particular weather conditions at particular week of the year.\nYou can write /start to begin a dialog.\nThen I will ask you to send me the number of month and a day you are interested in.\nAfter that you should specify the range of mean daily temperature (in Celcius) and the range of days with any precipitation per week that you prefer.\nEventually, you will get an image of the world map with all places found according to your criteria and links to Google map for at least five of them.\nYou can send /start at any time to start over again.\nType /help to read these instructions again.')

@bot.message_handler(commands=["start"])
def user_start(message):
    uid = message.chat.id
    reset_user(uid)
    bot.send_message(uid, 'Give me the number of month, please [1-12]')
    set_param(uid, 'state', config.States.S_MONTH.value)

@bot.message_handler(func=lambda message: get_param(message.chat.id, 'state') == config.States.S_MONTH.value)
def user_entering_day(message):
    uid = message.chat.id
    response = message.text
    if response.isdigit() and 1 <= int(response) <= 12:
        set_param(uid, 'month', response)
        set_param(uid, 'last_day_in_month', calendar.monthrange(2020, get_param(uid, 'month'))[1])
        bot.send_message(uid, "Give me the day, please [1-%s]" % get_param(uid, 'last_day_in_month'))
        set_param(uid, 'state', config.States.S_DAY.value)
    else:
        bot.send_message(uid, 'Something went wrong.\nSend me the correct number of month, please [1-12]')

@bot.message_handler(func=lambda message: get_param(message.chat.id, 'state') == config.States.S_DAY.value)
def user_entering_tmpr(message):
    uid = message.chat.id
    response = message.text
    if response.isdigit() and 1 <= int(response) <= get_param(uid, 'last_day_in_month'):
        set_param(uid, 'day', response)
        df_filtered_week, tmpr_min, tmpr_max = get_tmpr(uid, config.df_file, get_param(uid, 'month'), get_param(uid, 'day'))
        set_param(uid, 'df_filtered_week', df_filtered_week)
        set_param(uid, 'tmpr_min', tmpr_min)
        set_param(uid, 'tmpr_max', tmpr_max)
        bot.send_message(uid, "Give me a comma-delimited range of mean temperature you are looking for, please (in \u00b0C). For example: -10, -2 or 15, 15.\nActual range in the world for time you've chosen is: [{}, {}]".format(get_param(uid, 'tmpr_min'), get_param(uid, 'tmpr_max')))
        set_param(uid, 'state', config.States.S_TEMP.value)
    else:
        bot.send_message(uid, "Something went wrong.\nSend me the correct day, please [1-%s]" % get_param(uid, 'last_day_in_month'))

@bot.message_handler(func=lambda message: get_param(message.chat.id, 'state') == config.States.S_TEMP.value)
def user_entering_prcp(message):
    uid = message.chat.id
    response = message.text
    good_response = False
    try:
        tmpr_min_desired, tmpr_max_desired = [int(i.strip()) for i in response.split(',')]
        good_response = True
    except ValueError:
        pass
    if good_response and tmpr_min_desired <= get_param(uid, 'tmpr_max') and tmpr_max_desired >= get_param(uid, 'tmpr_min') and tmpr_min_desired <= tmpr_max_desired:
        set_param(uid, 'tmpr_min_desired', tmpr_min_desired)
        set_param(uid, 'tmpr_max_desired', tmpr_max_desired)
        df_filtered_tmpr, prcp_min, prcp_max = get_prcp(uid, get_param(uid, 'df_filtered_week'), get_param(uid, 'tmpr_min_desired'), get_param(uid, 'tmpr_max_desired'))
        set_param(uid, 'df_filtered_tmpr', df_filtered_tmpr)
        set_param(uid, 'prcp_min', prcp_min)
        set_param(uid, 'prcp_max', prcp_max)
        bot.send_message(uid, "Give me a comma-delimited range of the number of days with any kind of precipitation per week you prefer. For example: 2, 5 or 0, 0.\nBy precipitation I mean any of the following: rain, snow, hail or thunder.\nActual range of the number of such days per week in the world for chosen time and temperature range is [{}, {}]".format(get_param(uid, 'prcp_min'), get_param(uid, 'prcp_max')))
        set_param(uid, 'state', config.States.S_PREC_DAYS.value)
    elif good_response and tmpr_min_desired > tmpr_max_desired:
        bot.send_message(uid, "You've probably mismatched minimum and maximum temperature.\nPlease, send me the correct temperature range from minimum to maximum (in \u00b0C). For example: -20, -10 or 15, 15.\nActual range in the world for time you've chosen is: [{}, {}]".format(get_param(uid, 'tmpr_min'), get_param(uid, 'tmpr_max')))
    elif good_response and ('tmpr_min_desired' > get_param(uid, 'tmpr_max') or tmpr_max_desired < get_param(uid, 'tmpr_min')):
        bot.send_message(uid, "There are no places with such temperature range in the world for the chosen time.\nPlease, send me the correct temperature range (in \u00b0C).\nActual range in the world for time you've chosen is: [{}, {}]. Or type /start to start from the beginning".format(get_param(uid, 'tmpr_min'), get_param(uid, 'tmpr_max')))
    else:
        bot.send_message(uid, "Something went wrong.\nSend me the correct temperature range from minimum to maximum (in \u00b0C), please. For example: -20, -10 or 15, 15.\nActual range in the world for time you've chosen is: [{}, {}]".format(get_param(uid, 'tmpr_min'), get_param(uid, 'tmpr_max')))

@bot.message_handler(func=lambda message: get_param(message.chat.id, 'state') == config.States.S_PREC_DAYS.value)
def user_entering_prcp(message):
    uid = message.chat.id
    response = message.text
    good_response = False
    try:
        prcp_min_desired, prcp_max_desired = [int(i.strip()) for i in response.split(',')]
        good_response = True
    except ValueError:
        pass
    if good_response and prcp_min_desired <= get_param(uid, 'prcp_max') and prcp_max_desired >= get_param(uid, 'prcp_min') and 0 <= prcp_min_desired <= prcp_max_desired:
        set_param(uid, 'prcp_min_desired', prcp_min_desired)
        set_param(uid, 'prcp_max_desired', prcp_max_desired)
        set_param(
            uid,
            'df_filtered_final',
            get_final(
                uid,
                get_param(uid, 'df_filtered_tmpr'),
                get_param(uid, 'prcp_min_desired'),
                get_param(uid, 'prcp_max_desired')
            )
        )
        map_file, record_count, places, urls = get_results(uid, get_param(uid, 'df_filtered_final'))
        set_param(uid, 'map', map_file)
        set_param(uid, 'record_count', record_count)

        bot.send_message(uid, "Here is a map with all records I've found for you:")
        bot.send_photo(uid, open(get_param(uid, 'map'), 'rb'))

        bot.send_message(uid, "There are %s unique places in the world with parameters of your choice.\nHere are some of them:" % get_param(uid, 'record_count'))
        
        for i in range(len(urls)):
            set_param(uid, 'url', urls[i])
            set_param(uid, 'place', places[i])
            bot.send_message(uid, "{}: {}".format(get_param(uid, 'place'), get_param(uid, 'url')))
            
        bot.send_message(uid, "Good luck! Have a nice trip!")
        bot.send_message(uid, "Type /start to begin a new dialog.\nType /help for instructions.")

        set_param(uid, 'state', config.States.S_START.value)
        reset_user(uid)
        #bot.send_message(uid, "Debug info:" + get_user_info(uid))

    elif good_response and prcp_min_desired > prcp_max_desired:
        bot.send_message(uid, "You've probably mismatched minimum and maximum number of days.\nPlease, send me the correct range from minimum to maximum. For example: 2, 5 or 0, 0.\nActual range in the world for time you've chosen is: [{}, {}]".format(get_param(uid, 'prcp_min'), get_param(uid, 'prcp_max')))
    elif good_response and (prcp_min_desired > get_param(uid, 'prcp_max') or prcp_max_desired < get_param(uid, 'prcp_min')):
        bot.send_message(uid, "There are no places with such number of days with precipitation in the world for the chosen time and temperature.\nPlease, send me the correct range.\nActual range in the world for time you've chosen is: [{}, {}].\nOr type /start to start from the beginning".format(get_param(uid, 'prcp_min'), get_param(uid, 'prcp_max')))
    else:
        bot.send_message(uid, "Something went wrong.\nSend me the range of the number of days with precipitation per week, please. For example: 2, 5 or 0, 0.\nActual range of the number of such days per week in the world for chosen time and temperature range is [{}, {}]".format(get_param(uid, 'prcp_min'), get_param(uid, 'prcp_max')))


@bot.message_handler(func=lambda message: message.text not in ('/start', '/help'))
def user_entering_smth(message):
    uid = message.chat.id
    bot.send_message(uid, "Hello, I am a WhereIsWeatherBot!\n"
                                      "I can find places in the world with particular weather conditions at particular time of the year.\n"
                                      "Type /start and let me find those places for you.\n"
                                      "Type /help for instructions.")

if __name__ == '__main__':
    bot.polling(none_stop=True)
