from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import re

# Replace 'YOUR_TOKEN_HERE' with the token you got from BotFather
TOKEN = '7529101956:AAHTYrB3TwH18GOv4IEtZJ-u53v0_GaW840'

# Function to handle the /start command
def start(update, context):
    update.message.reply_text(
        "Hello! I'm your English Practice bot. Type a sentence, ask a question, or say 'help' for assistance."
    )

# Function to handle general inquiries and provide responses
def handle_message(update, context):
    user_message = update.message.text.lower()

    if re.search(r'\bwhat does (.+?) mean\b', user_message):
        word = re.search(r'\bwhat does (.+?) mean\b', user_message).group(1)
        response = f"The word '{word}' can mean various things depending on context. Let’s explore it together!"
    elif re.search(r'\bwhat are some synonyms for (.+?)\b', user_message):
        word = re.search(r'\bwhat are some synonyms for (.+?)\b', user_message).group(1)
        response = f"Some synonyms for '{word}' include 'excellent,' 'great,' and 'awesome.' Want to practice using them?"
    else:
        response = f"You said: {user_message}. Let's keep practicing!"

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

    # Keep the bot running until interrupted
    updater.idle()

if __name__ == '__main__':
    main()
