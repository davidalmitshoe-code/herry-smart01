from telegram import (
    Update,
    WebAppInfo,
    KeyboardButton,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import logging
import json

# ==========================
# SYSTEM SETUP & LOGGING
# ==========================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# CONFIGURATION CREDENTIALS
TOKEN = "8820217071:AAGltetsRpmnq4OG_osBdHH5pcvL0EJNdG4"
ADMIN_ID = 998942116
WEBAPP_URL = "https://davidalmitshoe-code.github.io/herry-smart01/"

# ==========================
# COMMAND INTERACTION ROUTER
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Setup bottom panel shortcut persistent keyboard menu button
    keyboard = [
        [
            KeyboardButton(
                text="🛍️ Open Herry Store", 
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Complete text introducing Herry Mobile & Accessories
    welcome_text = (
        "📱 Welcome to Herry Mobile & Accessories!\n\n"
        "We offer premium smartphones, stylish eye glasses, phone accessories, "
        "and custom suction stickers delivered directly to your location.\n\n"
        "✨ HOW IT WORKS:\n"
        "1. Tap 'Open Herry Store' below.\n"
        "2. Your Telegram username is automatically set as your default delivery locator!\n"
        "3. Simply prompt your Name & Phone, choose your items, and click ORDER NOW.\n\n"
        "👇 Open the catalog below to place your secure order instantly:"
    )
    
    await update.message.reply_text(text=welcome_text, reply_markup=reply_markup)

# ==========================
# WEBAPP PACKET DATA PARSER
# ==========================
async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Secure raw string transmission ingestion
        raw_string = update.effective_message.web_app_data.data
        logger.info(f"Incoming JSON Stream: {raw_string}")
        
        order_package = json.loads(raw_string)
        
        # Destructure payload object parameters
        name = order_package.get("name")
        phone = order_package.get("phone")
        place = order_package.get("place")  # This will be their Telegram Username by default
        cart = order_package.get("cart", [])
        total = order_package.get("total", 0)
        
        user_meta = update.effective_user
        handle = f"@{user_meta.username}" if user_meta.username else "No Public Handle"

        # Explicit data parsing safety backup verification 
        if not name or not phone or not place:
            await update.message.reply_text("⚠️ Processing Error: Name and Phone entry fields must not be blank.")
            return

        # Compile and format chosen product listing items cleanly
        items_list_summary = ""
        for index, item in enumerate(cart, 1):
            title = item.get("name", "Electronic Item")
            cost = item.get("price", 0)
            items_list_summary += f"  {index}. {title} — {cost} ETB\n"

        # Build clean invoice metadata layout receipt for Admin Panel
        receipt_template = f"""
📦 NEW CUSTOMER INVOICE

👤 PROFILE INFRASTRUCTURE:
▪️ Customer: {name}
▪️ Contact Phone: {phone}
▪️ Delivery/Username: {place}
▪️ Telegram Account: {handle}

🛒 SELECTED ITEMS:
{items_list_summary if items_list_summary else '  No products selected.'}
💰 TOTAL CHARGE AMOUNT: {total} ETB
"""
        # Forward direct clean packet notification message to admin operations panel
        await context.bot.send_message(chat_id=ADMIN_ID, text=receipt_template)
        
        # Reply directly back to customer confirming order hand-off success
        success_message = (
            f"🎉 Order verified successfully, {name}!\n\n"
            f"Your order has been routed to our admin panel. We will verify your "
            f"delivery at {phone} shortly."
        )
        await update.message.reply_text(text=success_message)

    except Exception as error:
        logger.error(f"Error handling webhook data stream: {error}")
        await update.message.reply_text("⚠️ Internal Server Error processing your invoice packet. Please try again.")

# ==========================
# APPLICATION ENGINE SETUP
# ==========================
def main():
    # Build wrapper app configuration pool instance
    app = Application.builder().token(TOKEN).build()
    
    # Handlers Registration routing infrastructure mapping
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))
    
    print("🤖 Processing Loop Initialized. Herry Bot is Active...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
