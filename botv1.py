# telegram bot energyAPIbot for echo CO2 of electricity for locations

#%%
import telegram
import telegram.ext
import re
from random import randint
import requests
import json
from config import API_KEY_TELEGRAM,API_TOKEN_C02
import datetime
from datetime import datetime
import requests
from tracemalloc import BaseFilter

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
Buttons_location_only=[telegram.KeyboardButton('Send location',request_location=True)]
Buttons_sendmore=['Ok, bye!','I want to know more']
Location_markup=telegram.ReplyKeyboardMarkup([Buttons_location],resize_keyboard = True, one_time_keyboard=True) 
Location_only_markup=telegram.ReplyKeyboardMarkup([Buttons_location_only],resize_keyboard = True, one_time_keyboard=True) 
Sendmore_markup=telegram.ReplyKeyboardMarkup([Buttons_sendmore],resize_keyboard = True, one_time_keyboard=True) 


# API function
def get_CO2(lon,lat):
    url = "https://api-access.electricitymaps.com/tw0j3yl62nfpdjv4/carbon-intensity/forecast?lon="+str(lon)+"&lat="+str(lat)
    headers = {
    "X-BLOBR-KEY": API_TOKEN_C02
    }
    response = requests.get(url, headers=headers)
    data= dict(response.json())
    forecast= data['forecast']
    carbForecast=[]
    dateForecast=[]
    hourForecast=[]
    for i in range(0,len(forecast)):
        carbForecast += [forecast[i]['carbonIntensity']]
        dateForecast += [forecast[i]['datetime']]
        hourForecast += [datetime.strptime(forecast[i]['datetime'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%H:%M')]

    n_hours=6
    levelForecast=list(int(1+(4*(carbForecast[i]-min(carbForecast[0:n_hours]))/(max(carbForecast[0:n_hours])-min(carbForecast[0:n_hours])))) for i in range(0,n_hours))
    text= list('H '+(str(hourForecast[i])+' '+str(carbForecast[i])+'g  '+'🔴'*int(levelForecast[i])) for i in range(0,n_hours))
    'In gCO2/kWh: \n'+'\n'.join(text[0:n_hours])
    msg1 = 'Where you are, the carbon intensity in the next hours will be (in gCO2/kWh): \n'+'\n'.join(text[0:n_hours])
    if carbForecast.index(min(carbForecast))==0:
        msg2= '\n\nThis means that if you do your washing machine now, instead that at '+ str(hourForecast[carbForecast.index(max(carbForecast))])+', instead of now, you could contribute saving '+ str(max(carbForecast)-carbForecast[0]) +' grams of CO2, assuming a typical consumption of 1 kWh'
    else:
        msg2= '\n\nThis means that if you do your washing machine at '+ str(hourForecast[carbForecast.index(min(carbForecast))])+', instead of now, you could contribute saving '+ str(carbForecast[0]-min(carbForecast)) +' grams of CO2 (assuming a typical consumption of 1 kWh)'
        
    message=msg1+msg2
    
    return message




# The entry function
def start(update_obj, context):
    # send the question, and show the keyboard markup (suggested answers)
    first_name = update_obj.message.from_user['first_name']
    update_obj.message.reply_text("Hi, I am energy bot, I can tell you how green is to consume electricity in the next hours based on where you live. Send me your location!",
        reply_markup=Location_markup
    )
    # go to the WELCOME state
    location = update_obj.message.location
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
        f"Okay, take care, {first_name}! If you want to use me again, just send me your location!", reply_markup=Location_only_markup
        )
        return SEND



def sendmore(update_obj, context):
    if update_obj.message.text=='I want to know more':
        update_obj.message.reply_text(
            f"This bot is open source and bilt by pienone. See more or contribute at https://github.com/pienone/EnergyBot). It is made possible thanks to the CO2signal API service, which provides forecasts of energy production data."
            )
        first_name = update_obj.message.from_user['first_name']
        update_obj.message.reply_text(
        f"Well, take care, {first_name}! If you want to use me again, just send me your location!", reply_markup=Location_only_markup        
        )
        return SEND
    else:
        first_name = update_obj.message.from_user['first_name']
        update_obj.message.reply_text(
        f"Okay, take care, {first_name}! If you want to use me again, just send me your location!", reply_markup=Location_only_markup
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
