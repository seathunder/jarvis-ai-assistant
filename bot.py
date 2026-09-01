from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, logger
import memory
from dispatcher import process_prompt

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    memory.save_message(user.id, "system", "User started the bot.")
    await update.message.reply_text(f"Hello {user.first_name}! I am Jarvis, your autonomous assistant. How can I help you today?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Send me any request, and my Dispatcher will triage and route it to the appropriate execution pipeline.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages."""
    user = update.effective_user
    user_prompt = update.message.text
    
    # Save user message to memory
    memory.save_message(user.id, "user", user_prompt)
    logger.info(f"Received message from {user.first_name}: {user_prompt}")
    
    # Optional: Send a 'typing' action to show it's working
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    # Fetch recent context (optional, passing to dispatcher later if needed)
    context_msgs = memory.get_recent_messages(user.id, limit=5)
    
    # Process the prompt via the Dispatcher
    response_text = process_prompt(user_prompt, context=context_msgs)
    
    # Save bot response to memory
    memory.save_message(user.id, "assistant", response_text)
    
    # Send the response back to the user
    await update.message.reply_text(response_text)

def main():
    """Start the bot."""
    # Initialize the database
    memory.init_db()
    
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Cannot start bot without TELEGRAM_BOT_TOKEN")
        return

    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - handle the message
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    logger.info("Starting Jarvis Telegram Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
