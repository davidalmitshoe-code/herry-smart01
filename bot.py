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
# LOGGING
# ==========================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==========================
# CONFIGURATION
# ==========================
TOKEN = "8820217071:AAGltetsRpmnq4OG_osBdHH5pcvL0EJNdG4"
ADMIN_ID = 998942116
WEBAPP_URL = "https://davidalmitshoe-code.github.io/herry-smart01/"

# ==========================
# START COMMAND
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Use a regular reply keyboard button. This is CRITICAL for sendData to work!
    keyboard = [
        [
            KeyboardButton(
                text="🛒 Open Herry Shop",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]
    ]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "📱 Welcome to Herry Mobile & Electronics!\n\n"
        "Click the button below at the bottom of your screen to open our shop, register, and place your order.",
        reply_markup=reply_markup
    )

# ==========================
# RECEIVE WEBAPP DATA
# ==========================
async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        raw_data = update.effective_message.web_app_data.data
        logger.info(f"RAW DATA RECEIVED: {raw_data}")

        order_info = json.loads(raw_data)
        
        # Extract Customer Info from WebApp Form
        customer_name = order_info.get("name", "Not Provided")
        customer_phone = order_info.get("phone", "Not Provided")
        customer_place = order_info.get("place", "Not Provided")
        
        # Extract Cart Info
        cart = order_info.get("cart", [])
        total = order_info.get("total", 0)
        
        # Telegram Username
        tg_user = update.effective_user
        username = f"@{tg_user.username}" if tg_user.username else "No Username"

        # Format products
        products_text = ""
        for item in cart:
            name = item.get("name", "Unknown Product")
            price = item.get("price", 0)
            products_text += f"• {name} - {price} ETB\n"

        # Combined Admin Message
        admin_message = f"""
🛍️ NEW ORDER & CUSTOMER REGISTRATION

👤 CUSTOMER INFO:
Name: {customer_name}
Phone: {customer_phone}
Delivery Place: {customer_place}
Telegram: {username}

📦 ORDER DETAILS:
{products_text if products_text else 'No products selected'}
💰 Total: {total} ETB
"""

        # Send to Admin
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)

        # Confirm to Customer
        await update.message.reply_text(
            f"✅ Thank you {customer_name}! Your order and registration info have been sent to the admin successfully."
        )

    except Exception as e:
        logger.error(f"WEBAPP PROCESSING ERROR: {e}")
        await update.message.reply_text("❌ Failed to process order. Please try again.")

# ==========================
# MAIN
# ==========================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))

    print("✅ Bot is actively running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
