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

# 🌍 PRODUCTION HOSTING URL 
# Replace this with your actual Render URL (e.g., https://herry-store-bot.onrender.com)
RENDER_WEB_URL = " https://herry-ngeb.onrender.com" 

# Initialize Flask App Engine
flask_app = Flask(__name__)

# Initialize Telegram Application Engine
tg_app = Application.builder().token(TOKEN).build()

# Temporary In-Memory State Database (To track chat steps)
USER_STATE = {}
USER_DATA = {}

# State Constants for Registration Flow
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
    USER_DATA[user_id] = {} # Initialize empty data for user
    
    await update.message.reply_text(
        "👋 Welcome to Herry Mobile & Accessories!\n\n"
        "To get started, please enter your Full Name:",
        reply_markup=ReplyKeyboardRemove()
    )

async def handle_registration_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = USER_STATE.get(user_id)
    text = update.message.text.strip()

    if user_id not in USER_DATA:
        USER_DATA[user_id] = {}

    # Step A: Capture Full Name Input
    if current_state == STATE_NAME:
        USER_DATA[user_id]["name"] = text
        USER_STATE[user_id] = STATE_PHONE
        await update.message.reply_text("Great! Now please enter your **Phone Number** 📞:")
        return

    # Step B: Capture Phone Number Input
    elif current_state == STATE_PHONE:
        USER_DATA[user_id]["phone"] = text
        USER_STATE[user_id] = STATE_PLACE
        await update.message.reply_text("Excellent! Finally, please enter your **Delivery Place / Location** 📍:")
        return

    # Step C: Capture Delivery Place Input
    elif current_state == STATE_PLACE:
        USER_DATA[user_id]["place"] = text
        USER_STATE[user_id] = STATE_READY

        # Registration Success Welcome Announcement Layout
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
        
        # Pull registration variables entirely from the chat memory database
        saved_info = USER_DATA.get(user_id, {})
        name = saved_info.get("name", "Unknown Profile")
        phone = saved_info.get("phone", "No Contact Phone")
        place = saved_info.get("place", "No Location Specified")
        
        cart = order_package.get("cart", [])
        total = order_package.get("total", 0)
        
        user_meta = update.effective_user
        handle = f"@{user_meta.username}" if user_meta.username else "No Username"

        # Compile and format chosen product listing items with standard counting numbers
        items_list_summary = ""
        for index, item in enumerate(cart, 1):
            title = item.get("name", "Electronic Item")
            cost = item.get("price", 0)
            items_list_summary += f"{index}. {title} — {cost} ETB\n"

        # Your exact customer layout block format
        receipt_template = f"""📦 NEW CUSTOMER INVOICE

👤 PROFILE INFRASTRUCTURE:
▪️ Customer: {name}
▪️ Contact: {phone}
▪️ Location: {place}
▪️ Telegram: {handle}

🛒 SELECTED ITEMS:
{items_list_summary if items_list_summary else 'No products selected.'}
💰 TOTAL CHARGE AMOUNT: {total} ETB"""

        # Dispatches structured receipt block safely to Admin Chat Panel
        await context.bot.send_message(chat_id=ADMIN_ID, text=receipt_template)
        
        # Customer success response confirmation text
        await update.message.reply_text(
            f"🎉 Order received successfully, {name}!\n"
            f"Our team will process your order and contact you at {phone} shortly."
        )

    except Exception as error:
        logger.error(f"Error compiling webapp data packet: {error}")

# Register all bot command and message handlers
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_registration_messages))

# ==========================================
# 3. FLASK WEBHOOK ROUTES & RUN CONFIGURATION
# ==========================================

@flask_app.route("/", methods=["GET"])
def home_index():
    return "Herry Bot Webhook Server is Online! 🚀", 200
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook_handler():
    """Receives incoming live updates directly sent from Telegram servers"""
    try:
        json_payload = request.get_data().decode("utf-8")
        update = Update.de_json(json.loads(json_payload), tg_app.bot)
        
        # FIX: Force execution inside the active running loop thread context safely
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.create_task(tg_app.process_update(update))
        return "OK", 200
    except Exception as err:
        logger.error(f"Webhook update processing exception: {err}")
        return "Internal Error", 500
@flask_app.route("/set_webhook", methods=["GET"])
def setup_live_webhook():
    """Forces the exact valid Render URL straight to Telegram"""
    # Hardcoding the secure link directly to bypass any variable errors
    target_webhook_url = f"https://herry-ngeb.onrender.com/{TOKEN}"
    
    async def set_hook():
        async with tg_app:
            return await tg_app.bot.set_webhook(url=target_webhook_url)
            
    try:
        success = asyncio.run(set_hook())
        if success:
            return f"✅ Webhook Registered Successfully to URL: {target_webhook_url}", 200
        return "❌ Webhook Registration Failed.", 500
    except Exception as e:
        return f"❌ Error setting webhook registration setup: {e}", 500

if __name__ == "__main__":
    # Local fallback initialization for testing purposes
    asyncio.run(tg_app.initialize())
    flask_app.run(host="0.0.0.0", port=5000)
