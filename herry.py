import logging
import json
import asyncio
from flask import Flask, request
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# 1. LOGGING & CONFIGURATION
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "8820217071:AAGltetsRpmnq4OG_osBdHH5pcvL0EJNdG4"
ADMIN_ID = 998942116
WEBAPP_URL = "https://davidalmitshoe-code.github.io/herry-smart01/"
RENDER_WEB_URL = "https://herry-ngeb.onrender.com"

# 2. INITIALIZE FLASK & TELEGRAM APPS
flask_app = Flask(__name__)
tg_app = Application.builder().token(TOKEN).build()

# Create a dedicated background event loop for handling async operations inside Flask
bot_loop = asyncio.new_event_loop()

# Memory databases for registration flow
USER_STATE = {}
USER_DATA = {}

STATE_NAME, STATE_PHONE, STATE_PLACE, STATE_READY = 1, 2, 3, 4

# 3. TELEGRAM BOT CHAT CHANNELS LOGIC
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USER_STATE[user_id] = STATE_NAME
    USER_DATA[user_id] = {}
    await update.message.reply_text(
        "👋 Welcome to Herry Mobile & Accessories!\n\nTo get started, please enter your Full Name:",
        reply_markup=ReplyKeyboardRemove()
    )

async def handle_registration_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = USER_STATE.get(user_id)
    text = update.message.text.strip() if update.message.text else ""

    if user_id not in USER_DATA:
        USER_DATA[user_id] = {}

    if current_state == STATE_NAME:
        USER_DATA[user_id]["name"] = text
        USER_STATE[user_id] = STATE_PHONE
        await update.message.reply_text("Great! Now please enter your **Phone Number** 📞:")
        return
    elif current_state == STATE_PHONE:
        USER_DATA[user_id]["phone"] = text
        USER_STATE[user_id] = STATE_PLACE
        await update.message.reply_text("Excellent! Finally, please enter your **Delivery Place / Location** 📍:")
        return
    elif current_state == STATE_PLACE:
        USER_DATA[user_id]["place"] = text
        USER_STATE[user_id] = STATE_READY

        keyboard = [[KeyboardButton(text="🛍️ Open Herry Store", web_app=WebAppInfo(url=WEBAPP_URL))]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        welcome_billboard = (
            "✅ Registration Complete!\n\n"
            "🚀 Welcome to Herry Mobile & Accessories Store!\n\n"
            "📍 Visit our shop: Hossana Grace Plaza B12, Mobile Zone\n"
            "📞 Call us anytime at: 0922445514\n\n"
            "👇 Click the Open Herry Store button below!"
        )
        await update.message.reply_text(text=welcome_billboard, reply_markup=reply_markup)
        return

async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        order_package = json.loads(update.effective_message.web_app_data.data)
        saved_info = USER_DATA.get(user_id, {})
        
        name = saved_info.get("name", "Unknown Profile")
        phone = saved_info.get("phone", "No Contact Phone")
        place = saved_info.get("place", "No Location Specified")
        cart = order_package.get("cart", [])
        total = order_package.get("total", 0)
        handle = f"@{update.effective_user.username}" if update.effective_user.username else "No Username"

        items_list_summary = ""
        for index, item in enumerate(cart, 1):
            items_list_summary += f"{index}. {item.get('name')} (x{item.get('quantity', 1)}) — {item.get('price')} ETB\n"

        receipt_template = f"📦 NEW CUSTOMER INVOICE\n\n👤 PROFILE:\n▪️ Customer: {name}\n▪️ Contact: {phone}\n▪️ Location: {place}\n▪️ Telegram: {handle}\n\n🛒 ITEMS:\n{items_list_summary}\n💰 TOTAL: {total} ETB"
        
        await context.bot.send_message(chat_id=ADMIN_ID, text=receipt_template)
        await update.message.reply_text(f"🎉 Order received successfully, {name}! We will contact you at {phone} shortly.")
    except Exception as error:
        logger.error(f"Error handling webapp data packet: {error}")

# Attach all command routers to our engine application
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_registration_messages))

# Initialize the bot app engine *once* globally inside our custom background loop
bot_loop.run_until_complete(tg_app.initialize())

# 4. PRODUCTION WEBHOOK ENDPOINTS
@flask_app.route("/", methods=["GET"])
def home_index():
    return "Herry Bot Webhook Server is running stable. 🚀", 200

@flask_app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook_handler():
    """Receives live production traffic and pipes it securely into our single event loop"""
    try:
        json_payload = request.get_data().decode("utf-8")
        update = Update.de_json(json.loads(json_payload), tg_app.bot)
        
        # Safely execute the update inside the persistent background loop context
        bot_loop.run_until_complete(tg_app.process_update(update))
        return "OK", 200
    except Exception as err:
        logger.error(f"Webhook update routing failure: {err}")
        return "Internal Error", 500

@flask_app.route("/set_webhook", methods=["GET"])
def setup_live_webhook():
    """Registers your live Render hook link straight to Telegram's master API database"""
    target_webhook_url = f"{RENDER_WEB_URL}/{TOKEN}"
    try:
        success = bot_loop.run_until_complete(tg_app.bot.set_webhook(url=target_webhook_url))
        if success:
            return f"✅ Webhook Registered Successfully to URL: {target_webhook_url}", 200
        return "❌ Webhook Registration Failed.", 500
    except Exception as e:
        return f"❌ Error setting webhook: {e}", 500

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=5000)
