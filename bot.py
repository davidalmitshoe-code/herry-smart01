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
# SYSTEM SETUP
# ==========================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "8820217071:AAGltetsRpmnq4OG_osBdHH5pcvL0EJNdG4"
ADMIN_ID = 998942116
WEBAPP_URL = "https://davidalmitshoe-code.github.io/herry-smart01/"

# ==========================
# COMMAND INTERACTION
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Setup bottom panel persistent menu shortcut
    keyboard = [
        [
            KeyboardButton(
                text="🛍️ Open Herry Store",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "✨ Welcome to Herry Mobile & Electronics!\n\n"
        "Tap the button below to browse our inventory, update your address information, and check out securely.",
        reply_markup=reply_markup
    )

# ==========================
# WEBAPP PACKET PARSER
# ==========================
async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        raw_string = update.effective_message.web_app_data.data
        logger.info(f"Incoming Payload Stream: {raw_string}")

        order_package = json.loads(raw_string)
        
        # Destructure package values fields
        name = order_package.get("name", "Unknown Profile")
        phone = order_package.get("phone", "No Contact Phone")
        place = order_package.get("place", "No Location Specified")
        cart = order_package.get("cart", [])
        total = order_package.get("total", 0)
        
        user_meta = update.effective_user
        handle = f"@{user_meta.username}" if user_meta.username else "Private User Account"

        # Compute product inventory listing item lines
        items_list_summary = ""
        for index, item in enumerate(cart, 1):
            title = item.get("name", "Device Item")
            cost = item.get("price", 0)
            items_list_summary += f"{index}. {title} — {cost} ETB\n"

        receipt_template = f"""
📦 NEW CUSTOMER INVOICE

👤 PROFILE INFRASTRUCTURE:
▪️ Customer: {name}
▪️ Contact: {phone}
▪️ Location: {place}
▪️ Telegram: {handle}

🛒 SELECTED ITEMS:
{items_list_summary if items_list_summary else 'No products declared.'}
💰 TOTAL CHARGE AMOUNT: {total} ETB
"""
        # Forward direct notice message copy to operations panel
        await context.bot.send_message(chat_id=ADMIN_ID, text=receipt_template)

        # Notify active subscriber checkout validation success confirmation response
        await update.message.reply_text(
            f"🎉 Success, {name}!\n\nYour order has been transmitted. The store admin is reviewing your order details."
        )

    except Exception as error:
        logger.error(f"Failed parsing message payload execution state: {error}")
        await update.message.reply_text("⚠️ An error occurred parsing the invoice data. Please verify fields try again.")

# ==========================
# EXECUTION ROUTER
# ==========================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))

    print("🤖 Processing Loop Initialized...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
