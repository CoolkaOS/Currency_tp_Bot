import telegram
import datetime
import random
import requests
import json

from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters


TOKEN = '707090914:AAFOupGmBjkNIkaZp81IEflkHuDiZgbqOWk'

bot = telegram.Bot(token=TOKEN)
print(bot.get_me())

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

#today = str(datetime.date.today()-datetime.timedelta(days=1))
i = 0
while i >= 0:
    today = datetime.date.today()-datetime.timedelta(days=i)-datetime.timedelta(days=1)
    if today.weekday()!=5 and today.weekday()!=6:
        break
    else:
        i += 1
date_1 = str(today - datetime.timedelta(30))  ##input("Enter a date: ")
today = str(today)
date_2 = today##input("Enter a date: ")
dates = (date_1, date_2)

currencies={'USD', 'AUD', 'BGN', 'EUR', 'RUB'}


def time_plus(date):
    str1 = date
    str2 = datetime.datetime(int(str1[0:4]), int(str1[5:7]), int(str1[8:10]))
    str2 = str2 + datetime.timedelta(1)
    if str2.weekday()!= 5 and str2.weekday()!= 6:
        weekend = False
    else:
        weekend = True
    str1 = str(str2)[0:10]
    return str1, weekend


def dates_ft(date_1, date_2):
    date = date_1
    dates = [date]
    while date != date_2:
        if not time_plus(date)[1]:
            date = time_plus(date)[0]
            dates.append(date)
        else:
            date = time_plus(date)[0]
    print('dates_ft')
    return dates


def make_dict(date_1, date_2): ## отправить все направо
    parameters = {
        "base": "RUB",
        "start_at": date_1,
        "end_at": date_2,
        "symbols": currencies ## ADD ANOTHER


    }
    r = requests.get("https://api.exchangeratesapi.io/history", params = parameters)
    main_dictionary = {}
    main_dictionary = r.json()['rates']
    for item in main_dictionary:
        st = main_dictionary[item]
        for shit in st:
            st[shit] = 1 / float(st[shit])
            st[shit] = round(st[shit], 3)
    print('make_dict')
    return main_dictionary


def reverse(main_dictionary):
    li = []
    for item1 in main_dictionary:
        for item2 in main_dictionary[item1]:
            li.append(item2)
        break
    dic = {}
    for item1 in li:
        dic1 = {}
        for item2 in main_dictionary:
            dic1[item2] = main_dictionary[item2][item1]
        dic[item1] = dic1

    list_minax = []
    min_v = 100000.0
    max_v = 0.0
    list_minax = {}
    for item in dic:
        st = dic[item]
        for item2 in st:
            if float(st[item2]) >= max_v:
                max_v = float(st[item2])
            if float(st[item2]) <= min_v:
                min_v = float(st[item2])
        difference = max_v - min_v
        list_minax[item] = [max_v, min_v, round(difference, 3)]
        min_v = 100000.0
        max_v = 0.0
    print('reverse')
    return [dic, list_minax]

def date_to_number(s):
    print('date_to_number')
    return int(s[8:10])+int(s[5:7])*31+int(s[0:4])*366-1995*366

def predict(currency):
    random.seed(date_to_number(today))
    s = random.randint(1, date_to_number(today))
    chosen_currency = reverse(make_dict(date_1, date_2))[0]
    ans = 0
    ans1 = chosen_currency[currency]['2018-11-01']
    way = 0
    for item1 in chosen_currency[currency]:
        delta = datetime.date(int(today[0:4]), int(today[5:7]), int(today[8:10])) - datetime.date(int(item1[0:4]),
                                                                                                  int(item1[5:7]),
                                                                                                  int(item1[8:10]))
        way += (chosen_currency[currency][item1] - ans1) / (delta.days + 1)
        ans1 = chosen_currency[currency][item1]
    ans = chosen_currency[currency][today] + (way*s) / (date_to_number(today))
    ans = round(ans, 3)
    print('predict')
    return ans


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="""I'm a Currency bot!
You can use these commands to interact with me:
/show_currencies.
/show and you put here some names of your currencies and two dates or dashes if you want to use basic date(one month early and today).
For example:
«/show <b>USD AUD 2018-10-10 2018-10-20</b>», or
«/show <b>USD - 2018-11-10</b>»,or
«/show <b>USD</b>».
/predict and put here some names of your currencies.
For example:
«/predict <b>USD AUD</b>».
/add and put here names of currencies you want to add to database.
For example:
«/add <b>GBP JPY</b>».
/convert and put value in first currency and pur here resulting currency.
For example:
«/convert <b>200 EUR in AUD</b>».""",parse_mode=telegram.ParseMode.HTML)
    print('start')
    updater.start_polling()


def print_curr():
    prompt = ''
    for curr in currencies:
        prompt += '\n'+curr
    print('print_curr')
    return prompt

def show_currency(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Exchange Rates are available for these currencies:'+print_curr())
    print('show_currency')


def predict_curr(bot, update, args):
    capitalize(args)
    args.append('N')
    if args != ['N']:
        args.pop(len(args)-1)
        for text in args:
            if text in currencies:
                bot.send_message(chat_id=update.message.chat_id, text=text+' exists, so')
                bot.send_message(chat_id=update.message.chat_id,text='For {} we have such prediction:\nTomorrow ExR for {} is {}'.format(text,text,predict(text)))
            else:
                bot.send_message(chat_id=update.message.chat_id,text='No such currency in our database as {}'.format(text),)
    else:
        bot.send_message(chat_id=update.message.chat_id,text='Wrong query.\n/add and put here names of currencies you want to add to database.\nFor example:\n«/add <b>GBP JPY</b>»',parse_mode=telegram.ParseMode.HTML )
    print('predict_curr')


def print_curr_exr(text, date_1, date_2):
    prompt = ''
    data = make_dict(date_1, date_2)
    for date in dates_ft(date_1,date_2):
        try:
            prompt += "{} : {}\n".format(date, data[date][text])
        except KeyError:
            prompt = prompt
    list_mmd = reverse(data)[1]
    prompt += 'Between {} and {}:\nMaximum ExR is {}.\nMinimum ExR is {}\nDifference is {}'.format(date_1,date_2,list_mmd[text][0],list_mmd[text][1],list_mmd[text][2])
    print('print_curr_exr')
    return prompt


def capitalize(list):
    for i in range(0, len(list)):
        list[i] = list[i].upper()
    print('capitalize')


def show_exr_currency(bot, update, args):
    dates1 = list(dates)
    try:
        try:
            if int(args[len(args)-2][0]):
                dates1[0] = args[len(args) - 2]
                args.pop(len(args)-2)
        except ValueError:
            dates1[0]=dates[0]
            if args[len(args)-2] == '-':
                args.pop(len(args)-2)
        try:
            if int(args[len(args) - 1][0]):
                dates1[1] = args[len(args) - 1]
                args.pop(len(args)-1)
        except ValueError:
            dates1[1]=dates[1]
            if args[len(args)-1] == '-':
                args.pop(len(args)-1)
    except IndexError:
        bot.send_message(chat_id=update.message.chat_id, text='Wrong query.\n/show and you mat put here some names of your currencies and two dates or dashes if you want to use basic date(one month early and today).\nFor example:\n«/show <b>USD AUD 2018-10-10 2018-10-20</b>» or\n«/show <b>USD - 2018-11-10</b>», or\n«/show <b>USD</b>».',parse_mode=telegram.ParseMode.HTML)
    #args=args[:len(args)-2]
    capitalize(args)
    for text in args:
        if text in currencies:
            bot.send_message(chat_id=update.message.chat_id, text=text+' exists, so:')
            try:
                bot.send_message(chat_id=update.message.chat_id, text=print_curr_exr(text,dates1[0],dates1[1]))
            except telegram.error.BadRequest:
                bot.send_message(chat_id=update.message.chat_id, text= 'Too long date gap.')
        else:
            bot.send_message(chat_id=update.message.chat_id, text='No such currency in our datebase as {}'.format(text),)
    print('show_exr_currency')


def no_idea(bot, update):
    update.message.reply_text("I'm sorry I do not understand you.")
    print('no_idea')


def stop(bot, update):
    updater.stop()


def add(bot, update, args):
    capitalize(args)
    args.append('')
    if args != ['']:
        args.pop(len(args)-1)
        for arg in args:
            try:
                currencies.add(arg)
                make_dict(date_1, date_2)
                update.message.reply_text('Currency {} added'.format(arg))
            except KeyError:
                update.message.reply_text('No such currency as {}'.format(arg))
                currencies.remove(arg)
    else:
        bot.send_message(chat_id=update.message.chat_id, text='Wrong query.\n/add and put here names of currencies you want to add to database.\nFor example:\n«/add <b>GBP JPY</b>»',parse_mode=telegram.ParseMode.HTML)


def conv(curr1, curr2, value):
    dic = reverse(make_dict(date_2, date_2))[0]
    new_value = value*dic[curr1][today]/dic[curr2][today]
    return round(new_value, 1)


def convert(bot, update, args):
    capitalize(args)
    try:
        cur1 = args[1]
        cur2 = args[3]
        value = float(args[0])
        update.message.reply_text('{} {} in {} is {}'.format(value, cur1, cur2, conv(cur1, cur2, value)))
    except IndexError:
        bot.send_message(chat_id=update.message.chat_id, text='Wrong query.\n/convert and put value in first currency and pur here resulting currency.\nFor example:\n«/convert <b>200 EUR in AUD</b>»',parse_mode=telegram.ParseMode.HTML)


main_dictionary = make_dict(date_1, date_2)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
updater.start_polling()

show_currency_handler = CommandHandler('show_currencies',show_currency)
dispatcher.add_handler(show_currency_handler)

check_input_currency_handler = CommandHandler('show', show_exr_currency,pass_args=True)
dispatcher.add_handler(check_input_currency_handler)

predict_curr_handler = CommandHandler('predict', predict_curr,pass_args=True)
dispatcher.add_handler(predict_curr_handler)

no_idea_handler = MessageHandler(Filters.text, no_idea)
dispatcher.add_handler(no_idea_handler)

stop_handler = CommandHandler('stop',stop)
dispatcher.add_handler(stop_handler)

add_curr_handler = CommandHandler('add',add,pass_args=True)
dispatcher.add_handler(add_curr_handler)

convert_handler = CommandHandler('convert',convert,pass_args=True)
dispatcher.add_handler(convert_handler)