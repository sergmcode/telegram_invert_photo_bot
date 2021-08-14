# import dotenv
import os

# dotenv.load_dotenv()
TOKEN = os.environ['TOKEN']
PORT = int(os.environ.get('PORT', '8443'))

print(TOKEN)
print(PORT)

from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Handler, CallbackContext
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update

import logging
import json

import requests as req

import os
from urllib.parse import urlparse

from telegram.ext.filters import Filters

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext):
    update.message.reply_text(text=f'''
hello <b> 😎 {update.effective_user.name} ! </b>
<b>Please send 🎄 me your picture</b>
''', parse_mode='HTML')

def process_photo(update: Update, context: CallbackContext):
    update.message.reply_text("Processing photo...")
    # print_update(update, None)
    photo_id = update.message.photo[-1].file_id
    url = context.bot.get_file(photo_id).file_path
    print(f'url: {url}')
    # file_name = f'photos/{os.path.basename(urlparse(url).path)}'
    file_name = os.path.basename(urlparse(url).path)
    resp = req.get(url)
    with open(file_name, 'wb') as f:
        f.write(resp.content)

    from PIL import Image
    import PIL.ImageOps    
    image = Image.open(file_name)

    if image.mode == 'RGBA':
        r,g,b,a = image.split()
        rgb_image = Image.merge('RGB', (r,g,b))
        inverted_image = PIL.ImageOps.invert(rgb_image)
        r2,g2,b2 = inverted_image.split()
        final_transparent_image = Image.merge('RGBA', (r2,g2,b2,a))
        final_transparent_image.save(file_name)
    else:
        inverted_image = PIL.ImageOps.invert(image)
        inverted_image.save(file_name)

    update.message.reply_photo(open(file_name, 'rb'), caption="This is your image inverted")

dispatcher.add_handler(CommandHandler('start', start))

dispatcher.add_handler(MessageHandler(Filters.photo, process_photo))

# Heroku will manage certificate and proxy automaticly
updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN,
                      webhook_url="https://telegram-invert-photo-bot.herokuapp.com/" + TOKEN)

updater.idle()