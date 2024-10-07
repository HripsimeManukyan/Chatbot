from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Replace 'YOUR_TOKEN_HERE' with the token you got from BotFather
TOKEN = '7529101956:AAHTYrB3TwH18GOv4IEtZJ-u53v0_GaW840'

# Function to handle the /start command
def start(update, context):
    update.message.reply_text("Hello! I'm your English Practice bot. Type a sentence and I will help you improve your English.")

# Function to handle messages (for conversation practice)
def handle_message(update, context):
    user_message = update.message.text
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
