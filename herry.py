import logging
import json
import asyncio
from flask import Flask, request
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Logging Setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Credentials Configuration
TOKEN = "8820217071:AAGltetsRpmnq4OG_osBdHH5pcvL0EJNdG4"
ADMIN_ID = 998942116
WEBAPP_URL = "https://davidalmitshoe-code.github.io/herry-smart01/"
RENDER_WEB_URL = "https://herry-ngeb.onrender.com"

# Initialize Engines
flask_app = Flask(__name__)
tg_app = Application.builder().token(TOKEN).build()

# Temporary In-Memory State Database
USER_STATE = {}
USER_DATA = {}

STATE_NAME = 1
STATE_PHONE = 2
STATE_PLACE = 3
STATE_READY = 4

# ==========================================
# 1. INITIAL START & REGISTRATION STEP FLOW
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USER_STATE[user_id] = STATE_NAME
    USER_DATA[user_id] = {}
    
    await update.message.reply_text(
        "👋 Welcome to Herry Mobile & Accessories!\n\n"
        "To get started, please enter your Full Name:",
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
            "Looking for high-quality electronics, glasses, or case protection? 📱🕶️🔌\n\n"
            "✨ With Herry Store you can:\n"
            "🚀 Get devices & items delivered quickly\n"
            "🍱 Choose from premium quality electronic options\n"
            "🎓 Enjoy student-friendly competitive pricing in Hossana\n\n"
            "📍 Visit our shop: Hossana Grace Plaza B12, Mobile Zone\n"
            "📞 Call us anytime at: 0922445514\n\n"
            "📢 Announcement:\n"
            "We have started priority device delivery directly to your Location!\n"
            "👇 Click the Open Herry Store button below!"
        )
        await update.message.reply_text(text=welcome_billboard, reply_markup=reply_markup)
        return

# ==========================================
# 2. WEBAPP COMPLETE ORDER PACKET PARSER
# ==========================================
async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        raw_string = update.effective_message.web_app_data.data
        order_package = json.loads(raw_string)
        
        saved_info = USER_DATA.get(user_id, {})
        name = saved_info.get("name", "Unknown Profile")
        phone = saved_info.get("phone", "No Contact Phone")
        place = saved_info.get("place", "No Location Specified")
        
        cart = order_package.get("cart", [])
        total = order_package.get("total", 0)
        
        user_meta = update.effective_user
        handle = f"@{user_meta.username}" if user_meta.username else "No Username"

        items_list_summary = ""
        for index, item in enumerate(cart, 1):
            title = item.get("name", "Electronic Item")
            cost = item.get("price", 0)
            qty = item.get("quantity", 1)
            items_list_summary += f"{index}. {title} (x{qty}) — {cost * qty} ETB\n"

        receipt_template = f"""📦 NEW CUSTOMER INVOICE

👤 PROFILE INFRASTRUCTURE:
▪️ Customer: {name}
▪️ Contact: {phone}
▪️ Location: {place}
▪️ Telegram: {handle}

🛒 SELECTED ITEMS:
{items_list_summary if items_list_summary else 'No products selected.'}
💰 TOTAL CHARGE AMOUNT: {total} ETB"""

        await context.bot.send_message(chat_id=ADMIN_ID, text=receipt_template)
        await update.message.reply_text(
            f"🎉 Order received successfully, {name}!\n"
            f"Our team will process your order and contact you at {phone} shortly."
        )
    except Exception as error:
        logger.error(f"Error compiling webapp data packet: {error}")

# Handlers Binding
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_registration_messages))

# ==========================================
# 3. PERMANENT PRODUCTION WEBHOOK MECHANISM
# ==========================================

@flask_app.route("/", methods=["GET"])
def home_index():
    return "Herry Bot Webhook Server is Online and Secure! 🚀", 200

@flask_app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook_handler():
    """Handles async loop orchestration perfectly under Gunicorn multi-threading"""
    try:
        json_payload = request.get_data().decode("utf-8")
        update = Update.de_json(json.loads(json_payload), tg_app.bot)
        
        # Pull or build a global thread loop to execute processing tasks permanently
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Ensure the background application instance state is fully loaded
        if not tg_app.updater:
            loop.run_until_complete(tg_app.initialize())
            
        loop.create_task(tg_app.process_update(update))
        return "OK", 200
    except Exception as err:
        logger.error(f"Critical execution error: {err}")
        return "Internal Error", 500

@flask_app.route("/set_webhook", methods=["GET"])
def setup_live_webhook():
    target_webhook_url = f"{RENDER_WEB_URL}/{TOKEN}"
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(tg_app.initialize())
        success = loop.run_until_complete(tg_app.bot.set_webhook(url=target_webhook_url))
        
        if success:
            return f"✅ Webhook Registered Successfully to URL: {target_webhook_url}", 200
        return "❌ Webhook Registration Failed.", 500
    except Exception as e:
        return f"❌ Error setting webhook registration setup: {e}", 500

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=5000)
