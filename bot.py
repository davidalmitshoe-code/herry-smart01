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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "8820217071:AAGltetsRpmnq4OG_osBdHH5pcvL0EJNdG4"
ADMIN_ID = 998942116
WEBAPP_URL = "https://davidalmitshoe-code.github.io/herry-smart01/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton(text="🛍️ Open Herry Store", web_app=WebAppInfo(url=WEBAPP_URL))]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "✨ Welcome to Herry Mobile & Electronics!\n\n"
        "Tap the button below to browse, enter your address, and place your order.",
        reply_markup=reply_markup
    )

async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        raw_string = update.effective_message.web_app_data.data
        order_package = json.loads(raw_string)
        
        name = order_package.get("name")
        phone = order_package.get("phone")
        place = order_package.get("place")
        cart = order_package.get("cart", [])
        total = order_package.get("total", 0)
        
        user_meta = update.effective_user
        handle = f"@{user_meta.username}" if user_meta.username else "No Telegram Username"

        # Extra safety validation backup on python server side
        if not name or not phone or not place:
            await update.message.reply_text("⚠️ Order blocked. You must provide Registration fields in your profile tab.")
            return

        items_list_summary = ""
        for index, item in enumerate(cart, 1):
            items_list_summary += f"  {index}. {item.get('name')} — {item.get('price')} ETB\n"

        receipt_template = f"""
📦 NEW ORDER RECEIVED

👤 CUSTOMER REGISTRATION INFO:
▪️ Name: {name}
▪️ Phone: {phone}
▪️ Location: {place}
▪️ Telegram Account: {handle}

🛒 ORDERED PRODUCTS:
{items_list_summary}
💰 TOTAL PAID AMOUNT: {total} ETB
"""
        # Send full data block package cleanly to Admin panel
        await context.bot.send_message(chat_id=ADMIN_ID, text=receipt_template)
        await update.message.reply_text(f"🎉 Order verified successfully, {name}! The admin is processing your transaction.")

    except Exception as error:
        logger.error(f"Error handling webhook submission: {error}")

def main():
    app = Application.builder().token(TOKEN).build()
    
    # FIX: Correctly registered handlers without the syntax typo
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))
    
    print("🤖 Processing Loop Initialized...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
