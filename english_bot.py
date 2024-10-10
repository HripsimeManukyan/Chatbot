import re
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = '7529101956:AAHTYrB3TwH18GOv4IEtZJ-u53v0_GaW840'

# Dictionary to track user states
user_states = {}

# Function to handle the /start command
def start(update, context):
    user_id = update.message.chat_id
    user_states[user_id] = {'state': None, 'word': None}  # Initialize state properly
    update.message.reply_text(
        "Hello! I'm your Vocabulary Practice bot. Here's how you can interact with me:\n"
        "1. Ask for a word definition: Type 'What does [word] mean?'\n"
        "2. Ask for synonyms: Type 'What are some synonyms for [word]?' \n"
        "3. Practice using a word in a sentence after asking for synonyms or definitions.\n"
        "Try it out, and let's start learning!"
    )

# Function to fetch synonyms using the Datamuse API
def get_synonyms(word):
    url = f"https://api.datamuse.com/words?rel_syn={word}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        synonyms = [item['word'] for item in data]
        return synonyms
    else:
        return []

# Function to get word definition using an external API
def get_word_definition(word):
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            # Extract the definition and example
            if data and isinstance(data, list):
                meanings = data[0].get('meanings', [])
                if meanings:
                    definitions_list = meanings[0].get('definitions', [])
                    if definitions_list:
                        definition = definitions_list[0].get('definition', 'No definition available.')
                        example = definitions_list[0].get('example', 'No example available.')
                        return f"The word '{word}' means: {definition}\nExample: {example}\n\nCan you use '{word}' in a sentence?"
            return f"Sorry, I couldn't find a valid definition for '{word}'."
        else:
            return f"Sorry, I couldn't retrieve the definition for '{word}' at the moment."
    except Exception as e:
        return f"An error occurred while retrieving the definition: {e}"

# Function to handle user messages
def handle_message(update, context):
    user_id = update.message.chat_id
    user_message = update.message.text.lower()

    # Check if the user is in practice mode
    if user_id in user_states and user_states[user_id]['state'] == 'practice_word':
        state_info = user_states[user_id]
        if state_info['word'] in user_message:
            response = f"Great job! You used '{state_info['word']}' correctly in a sentence. Do you want to practice another word or ask for synonyms?"
            update.message.reply_text(response)
            user_states[user_id] = {'state': None, 'word': None}  # Reset state
        else:
            response = f"Let's keep practicing! Try using '{state_info['word']}' in a sentence."
            update.message.reply_text(response)
        return

    # Check for word definitions
    if re.search(r'\bwhat does (.+?) mean\b', user_message):
        word = re.search(r'\bwhat does (.+?) mean\b', user_message).group(1)
        word = word.strip('\'" ')  # Remove quotes and spaces
        response = get_word_definition(word)
        user_states[user_id] = {'state': 'practice_word', 'word': word}  # Set practice mode for definition
        update.message.reply_text(response)

    # Check for synonyms
    elif re.search(r'\bwhat are some synonyms for (.+?)\b', user_message):
        word = re.search(r'\bwhat are some synonyms for (.+?)\b', user_message).group(1)
        word = word.strip('\'" ')
        synonyms = get_synonyms(word)
        if synonyms:
            response = f"Some synonyms for '{word}' include {', '.join(synonyms)}. Want to practice using them?"
            user_states[user_id] = {'state': 'practice_synonym', 'word': word}  # Set practice mode for synonyms
        else:
            response = f"Sorry, I don't know any synonyms for '{word}'."
        update.message.reply_text(response)

    # If message doesn't match vocabulary queries, guide the user back
    else:
        response = (
            "You can ask me about word meanings or synonyms. Try typing:\n"
            "'What does [word] mean?' or 'What are some synonyms for [word]?'"
        )
        update.message.reply_text(response)

# Function to handle errors
def error(update, context):
    print(f"Update {update} caused error {context.error}")

def main():
    # Create the Updater and pass your bot's token
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register the /start command handler
    dp.add_handler(CommandHandler("start", start))

    # Register a message handler to process all text messages
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Log errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Print the port for debugging
    port = os.environ.get("PORT", 5000)
    print(f"Bot is running on port: {port}")

    # Keep the bot running until interrupted
    updater.idle()

if __name__ == '__main__':
    main()

