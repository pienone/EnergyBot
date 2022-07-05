
# 5422569643:AAHmXZqQNN74i7IvujsqSuUgbC1MGZAEg5A
# t.me/EnergyAPIbot

#%%

from telegram.ext import Updater, CommandHandler
import requests
import re

#%% bot

def get_url():
    contents = requests.get('https://random.dog/woof.json').json()    
    url = contents['url']
    return url


def bop(bot, update):
    url = get_url()
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=url)


def main():
    updater = Updater('YOUR_TOKEN')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('bop',bop))
    updater.start_polling()
    updater.idle()
    
if __name__ == '__main__':
    main()


#  def get_data():
#    content=request.get('')
#    GET https://api.electricitymap.org/v3/zones


#    contents = requests.get('https://api.electricitymap.org/v3/zones').json()

# %%
