import os
import telebot
from telebot import types
import subprocess

TOKEN = '7200872669:AAERLK_ZY72BEk181s_8bm3I7b6GeM4oe88'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Send me a Bash file (e.g., thingy.sh) to decrypt!')

@bot.message_handler(content_types=['document'])
def handle_document(message):
    document = message.document
    if not document.file_name.endswith('.sh'):
        bot.send_message(message.chat.id, 'Please send a valid Bash (.sh) file.')
        return

    file_info = bot.get_file(document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_path = os.path.join('downloads', document.file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    decryptor_script_path = './decryptor.sh'
    result = subprocess.run(['bash', decryptor_script_path, file_path], capture_output=True, text=True)

    if result.returncode == 0:
        with open(file_path, 'rb') as decrypted_file:
            bot.send_document(message.chat.id, decrypted_file, caption=f'Thanks to @Vano_Ganzzz \n \n')
    else:
        bot.send_message(message.chat.id, 'Failed to decrypt the file.')
        print(result.stderr)

    os.remove(file_path)

bot.polling()
