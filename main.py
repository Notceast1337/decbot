import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import subprocess
from telegram.error import TimedOut, NetworkError

# Bot Token
TOKEN = '7200872669:AAHYqX6leq5dpED3G4-yAW_VomwB8twtBhQ'

# Initialize the bot
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
executor = ThreadPoolExecutor(max_workers=10)  # Adjust the number of workers based on your needs

# Dictionary to track user file processing status
user_processing = {}

# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    gif_url = 'https://i.pinimg.com/originals/c2/ce/2d/c2ce2d82a11c90b05ad4abd796ef2fff.gif'
    context.bot.send_animation(chat_id=update.effective_chat.id, animation=gif_url, caption='Welcome, Send me a Bash (.sh) or Shell Compiler (.shc) file to decrypt!')

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# Helper function to handle decryption
def decrypt_file(file_path, chat_id, bot, process_message_id, user_id):
    def run_decryption():
        decryptor_script_path = './decryptor.sh'
        result = subprocess.run(['bash', decryptor_script_path, file_path], capture_output=True, text=True)
        
        with open(file_path, 'rb') as decrypted_file:
            decrypted_data = decrypted_file.read()
        
        if len(decrypted_data) == 0:
            update_status(bot, chat_id, process_message_id, 'Failed to decrypt the file.')
            delete_file(file_path)  # Delete the file if decryption failed
        else:
            gif_url = 'https://www.icegif.com/wp-content/uploads/2023/08/icegif-727.gif'
            send_with_retry(bot.send_animation, chat_id=chat_id, animation=gif_url)

            update_status(bot, chat_id, process_message_id, 'Decryption complete!')
            send_with_retry(bot.send_document, chat_id=chat_id, document=open(file_path, 'rb'))
            delete_file(file_path)  # Delete the file after successful decryption
        
        # Mark the user's file processing as complete
        user_processing[user_id] = False

    def delete_file(file_path):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"File {file_path} successfully deleted.")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

    def update_status(bot, chat_id, message_id, text):
        for _ in range(3):  # Try up to 3 times
            try:
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text)
                break
            except (TimedOut, NetworkError) as e:
                print(f"Error updating status: {e}")
                time.sleep(2)  # Wait before retrying

    def send_with_retry(func, *args, **kwargs):
        for _ in range(3):  # Try up to 3 times
            try:
                func(*args, **kwargs)
                break
            except (TimedOut, NetworkError) as e:
                print(f"Error sending message: {e}")
                time.sleep(2)  # Wait before retrying

    # Run decryption in a separate thread
    decryption_thread = threading.Thread(target=run_decryption)
    decryption_thread.start()

    # Wait for 10 seconds
    decryption_thread.join(timeout=15)

    # Check if the decryption thread is still alive after 10 seconds
    if decryption_thread.is_alive():
        update_status(bot, chat_id, process_message_id, 'Failed to decrypt the file. Timeout exceeded.')
        delete_file(file_path)  # Delete the file if decryption timed out
        user_processing[user_id] = False

# Document handler
def handle_document(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_processing.get(user_id, False):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Please wait until your previous file is processed.')
        return

    if update.message and update.message.document:
        document = update.message.document
        file_name = document.file_name

        if not file_name.endswith('.sh') and not file_name.endswith('.shc') and not file_name.endswith('.js'):
            context.bot.send_message(chat_id=update.effective_chat.id, text='Please send a valid Bash (.sh), Shell Compiler (.shc), or JavaScript (.js) file.')
            return

        file_info = context.bot.get_file(document.file_id)
        file_path = os.path.join('downloads', file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        file_info.download(file_path)
        
        if file_name.endswith('.sh') or file_name.endswith('.shc'):
            process_message = context.bot.send_message(chat_id=update.effective_chat.id, text='Decrypting the code...')
            
            # Mark the user's file processing as in progress
            user_processing[user_id] = True
            
            # Submit decryption task to the executor
            executor.submit(decrypt_file, file_path, update.effective_chat.id, context.bot, process_message.message_id, user_id)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='No document found in the message.')

document_handler = MessageHandler(Filters.document, handle_document)
dispatcher.add_handler(document_handler)

# Start polling
updater.start_polling(drop_pending_updates=True)
updater.idle()
