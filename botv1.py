# telegram bot energyAPIbot for echo CO2 of electricity for locations

#%%
from tracemalloc import BaseFilter
import telegram
import telegram.ext
import re
from random import randint
import requests
import json
from config import API_KEY_TELEGRAM,API_TOKEN_C02

# Dispatcher
updater = telegram.ext.Updater(API_KEY_TELEGRAM)
dispatcher = updater.dispatcher

# States
SEND = 0
SENDMORE = 1
RESTART = 2
CANCEL= 3

# Buttons
Buttons_location=[telegram.KeyboardButton('Send location',request_location=True),'No, thanks']
Buttons_sendmore=['Ok, bye!','I want to know more']
Location_markup=telegram.ReplyKeyboardMarkup([Buttons_location],resize_keyboard = True, one_time_keyboard=True) 
Sendmore_markup=telegram.ReplyKeyboardMarkup([Buttons_sendmore],resize_keyboard = True, one_time_keyboard=True) 


# API function
def get_CO2(lon,lat):
    gethooks= "https://api.co2signal.com/v1/latest?lon="+str(lon)+"&lat="+str(lat)
    headers={"auth-token": API_TOKEN_C02}
    response = requests.get(gethooks, headers=headers)
    dict=response.json()
    message = "The carbon intensity at the moment is "+ str(dict['data']['carbonIntensity']) +" gCO2eq/kWh, while the fossil fuel percentage in the energy production mix is "+str(dict['data']['fossilFuelPercentage'])+" %!"
    return message




# The entry function
def start(update_obj, context):
    # send the question, and show the keyboard markup (suggested answers)
    first_name = update_obj.message.from_user['first_name']
    update_obj.message.reply_text("Hi, I am energy bot, I can tell you how green is to consume electricity in the next hours based on where you live. Send me your location!",
        reply_markup=Location_markup
    )
    # go to the WELCOME state
    return SEND



# in the WELCOME state, check if the user wants to answer a question
def send(update_obj, context):
    first_name = update_obj.message.from_user['first_name']
    location = update_obj.message.location
    if  update_obj.message.location != None:
        message=get_CO2(location['longitude'],location['latitude'])
        update_obj.message.reply_text(message, reply_markup=Sendmore_markup)
        return SENDMORE
    else:
        first_name = update_obj.message.from_user['first_name']
        update_obj.message.reply_text(
        f"Okay, take care, {first_name}! If you want to use me again, just send me your location!", reply_markup=telegram.ReplyKeyboardRemove()
        )
        return SEND



def sendmore(update_obj, context):
    if update_obj.message.text=='I want to know more':
        update_obj.message.reply_text(
            f"This bot is open source and built by pienone, it's made possible thanks to CO2signal APIs bla bla bla...."
            )
        first_name = update_obj.message.from_user['first_name']
        update_obj.message.reply_text(
        f"Okay, take care, {first_name}! If you want to use me again, just send me your location!", reply_markup=telegram.ReplyKeyboardRemove()        
        )
        return SEND
    else:
        first_name = update_obj.message.from_user['first_name']
        update_obj.message.reply_text(
        f"Okay, take care, {first_name}! If you want to use me again, just send me your location!", reply_markup=telegram.ReplyKeyboardRemove()
        )
        return SEND


def restart(update_obj, context):
    return SEND


def cancel(update_obj, context):
    return telegram.ext.ConversationHandler.END



# a regular expression that matches yes or no
yes_no_regex = re.compile(r'^(yes|no|y|n)$', re.IGNORECASE)
# Create our ConversationHandler, with only one state
handler = telegram.ext.ConversationHandler(
      entry_points=[telegram.ext.CommandHandler('start', start)],
      states={
            SEND: [telegram.ext.MessageHandler(telegram.ext.Filters.location | telegram.ext.Filters.text(Buttons_location),send)],
            SENDMORE: [telegram.ext.MessageHandler(telegram.ext.Filters.text(Buttons_sendmore), sendmore)],
            RESTART: [telegram.ext.MessageHandler(telegram.ext.Filters.location, restart)]
      },
      fallbacks=[telegram.ext.CommandHandler('cancel', cancel)],
      )


# add the handler to the dispatcher
dispatcher.add_handler(handler)

# start polling for updates from Telegram
updater.start_polling()

# block until a signal (like one sent by CTRL+C) is sent
updater.idle()


