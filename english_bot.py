import os
import re
import requests
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from googletrans import Translator
from flask import Flask, request

# Telegram Bot Token
TOKEN = 'your_telegram_bot_token'
app = Flask(__name__)

# Set your webhook URL
WEBHOOK_URL = 'https://chatbot-6-9y8n.onrender.com/webhook/' + TOKEN

# Dictionary to track user states
user_states = {}

# Initialize the Translator instance globally
translator = Translator()

# Function to set the webhook with Telegram
def set_webhook():
    response = requests.post(f'https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}')
    if response.status_code == 200:
        print(f"Webhook set successfully: {WEBHOOK_URL}")
    else:
        print(f"Failed to set webhook: {response.text}")

# Function to translate a word to Armenian
def translate_to_armenian(word):
    try:
        translation = translator.translate(word, dest='hy')
        return translation.text
    except Exception as e:
        return f"An error occurred while translating: {e}"

# Function to fetch synonyms using the Datamuse API
def get_synonyms(word):
    url = f"https://api.datamuse.com/words?rel_syn={word}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        synonyms = [item['word'] for item in data]

        if synonyms:
            # Translate the first synonym into Armenian (or any number of synonyms)
            translated_synonyms = [translate_to_armenian(synonym) for synonym in synonyms]
            return synonyms, translated_synonyms
        else:
            return [], []
    else:
        return [], []

# Function to fetch word definitions
def get_word_definition(word):
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if data and isinstance(data, list):
                meanings = data[0].get('meanings', [])
                if meanings:
                    definitions_list = meanings[0].get('definitions', [])
                    if definitions_list:
                        definition = definitions_list[0].get('definition', 'No definition available.')
                        example = definitions_list[0].get('example', 'No example available.')

                        # Get Armenian translation
                        armenian_translation = translate_to_armenian(word)

                        return (f"The word '{word}' means: {definition}\n"
                                f"Example: {example}\n\n"
                                f"Armenian Translation: {armenian_translation}\n\n"
                                "Can you use '{word}' in a sentence?")
            return f"Sorry, I couldn't find a valid definition for '{word}'."
        else:
            return f"Sorry, I couldn't retrieve the definition for '{word}' at the moment."
    except Exception as e:
        return f"An error occurred while retrieving the definition: {e}"

# Function to handle the /start command
async def start(update: Update, context):
    user_id = update.message.chat_id
    user_states[user_id] = {'state': None, 'word': None}  # Initialize state properly
    await update.message.reply_text(
        "Hello! I'm your Vocabulary Practice bot. Here's how you can interact with me:\n"
        "1. Ask for a word definition: Type 'What does [word] mean?'\n"
        "2. Ask for synonyms: Type 'What are some synonyms for [word]?' \n"
        "3. Practice using a word in a sentence after asking for synonyms or definitions.\n"
        "Try it out, and let's start learning!"
    )

# Function to handle user messages
async def handle_message(update: Update, context):
    user_message = update.message.text.lower()
    user_id = update.message.chat_id

    # Check for word synonyms request
    if re.search(r'\bwhat are some synonyms for (.+?)\b', user_message):
        word = re.search(r'\bwhat are some synonyms for (.+?)\b', user_message).group(1)
        word = word.strip('\'" ')
        synonyms, translated_synonyms = get_synonyms(word)
        if synonyms:
            response = (f"Some synonyms for '{word}' include {', '.join(synonyms)}.\n"
                        f"Armenian Translations: {', '.join(translated_synonyms)}\n"
                        "Want to practice using them?")
            user_states[user_id] = {'state': 'practice_synonym', 'word': word}
        else:
            response = f"Sorry, I don't know any synonyms for '{word}'."
        await update.message.reply_text(response)

    # Check for word definition request
    elif re.search(r'\bwhat does (.+?) mean\?\b', user_message):
        word = re.search(r'\bwhat does (.+?) mean\?\b', user_message).group(1)
        word = word.strip('\'" ')
        definition_response = get_word_definition(word)
        await update.message.reply_text(definition_response)

    else:
        await update.message.reply_text("I don't understand that command.")

# Function to handle errors
def error(update, context):
    print(f"Update {update} caused error {context.error}")

# Webhook route to handle Telegram updates
@app.route(f'/webhook/{TOKEN}', methods=['POST'])
def webhook():
    if request.method == 'POST':
        update = Update.de_json(request.get_json(force=True), app.bot)
        app.dispatcher.process_update(update)
        return "ok", 200

if __name__ == '__main__':
    # Initialize the Application (Updater has been deprecated)
    telegram_app = Application.builder().token(TOKEN).build()

    # Register handlers
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Log errors
    telegram_app.add_error_handler(error)

    # Set webhook when app starts
    set_webhook()

    # Start Flask app
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

