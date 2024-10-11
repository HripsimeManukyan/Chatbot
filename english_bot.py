import os
import re
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher
from telegram import Update
from flask import Flask, request

# Telegram Bot Token
TOKEN = '7529101956:AAHTYrB3TwH18GOv4IEtZJ-u53v0_GaW840'
app = Flask(__name__)

# Set your webhook URL
WEBHOOK_URL = 'https://chatbot-6-9y8n.onrender.com/webhook/' + TOKEN

# Dictionary to track user states
user_states = {}

# Initialize Telegram Updater and Dispatcher
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Function to set the webhook
def set_webhook():
    try:
        response = requests.get(WEBHOOK_URL)
        if response.status_code == 200:
            print("Webhook set successfully.")
        else:
            print(f"Failed to set webhook: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while setting the webhook: {e}")
# Function to fetch word definition
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

                        return (f"The word '{word}' means: {definition}\n"
                                f"Example: {example}\n\n"
                                "Can you use '{word}' in a sentence?")
            return f"Sorry, I couldn't find a valid definition for '{word}'."
        else:
            return f"Sorry, I couldn't retrieve the definition for '{word}' at the moment."
    except Exception as e:
        return f"An error occurred while retrieving the definition: {e}"

# Function to fetch synonyms
def get_synonyms(word):
    url = f"https://api.datamuse.com/words?rel_syn={word}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        synonyms = [item['word'] for item in data]

        if synonyms:
            return synonyms
        else:
            return []
    else:
        return []

# Function to handle the /start command
def start(update, context):
    user_id = update.message.chat_id
    user_states[user_id] = {'state': None, 'word': None}
    update.message.reply_text(
        "Hello! I'm your Vocabulary Practice bot. Here's how you can interact with me:\n"
        "1. Ask for a word definition: Type 'What does [word] mean?'\n"
        "2. Ask for synonyms: Type 'What are some synonyms for [word]?' \n"
        "3. Practice using a word in a sentence after asking for synonyms or definitions.\n"
        "Try it out, and let's start learning!"
    )

# Function to handle incoming messages and questions
def handle_message(update, context):
    user_message = update.message.text.lower()
    user_id = update.message.chat_id

    # Word Definition
    if re.search(r'\bwhat does (.+?) mean\b', user_message):
        word = re.search(r'\bwhat does (.+?) mean\b', user_message).group(1)
        word = word.strip('\'" ')
        response = get_word_definition(word)
        update.message.reply_text(response)

    # Synonyms Request
    elif re.search(r'\bwhat are some synonyms for (.+?)\b', user_message):
        word = re.search(r'\bwhat are some synonyms for (.+?)\b', user_message).group(1)
        word = word.strip('\'" ')
        synonyms = get_synonyms(word)
        if synonyms:
            response = (f"Some synonyms for '{word}' include {', '.join(synonyms)}.\n"
                        "Want to practice using them?")
            user_states[user_id] = {'state': 'practice_synonym', 'word': word}
        else:
            response = f"Sorry, I don't know any synonyms for '{word}'."
        update.message.reply_text(response)

    # Default response
    else:
        update.message.reply_text("I'm not sure how to help with that. You can ask me for word definitions or synonyms.")

# Function to handle errors
def error(update, context):
    print(f"Update {update} caused error {context.error}")

# Webhook route to handle Telegram updates
@app.route(f'/webhook/{TOKEN}', methods=['POST'])
def webhook():
    if request.method == 'POST':
        update = Update.de_json(request.get_json(force=True), updater.bot)
        dispatcher.process_update(update)
        return "ok", 200

if __name__ == '__main__':
    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Log errors
    dispatcher.add_error_handler(error)

    # Set webhook when app starts
    set_webhook()

    # Start Flask app
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

