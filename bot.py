import logging
import json
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

# Temporary In-Memory State Database (To track chat steps)
USER_STATE = {}
USER_DATA = {}

# State Constants
STATE_NAME = 1
STATE_PHONE = 2
STATE_READY = 3

# ==========================================
# 1. INITIAL START & REGISTRATION STEP FLOW
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USER_STATE[user_id] = STATE_NAME
    
    await update.message.reply_text(
        "👋 Welcome to Herry Mobile & Accessories!\n\n"
        "To get started, please enter your Full Name:",
        reply_markup=ReplyKeyboardRemove()
    )

async def handle_registration_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = USER_STATE.get(user_id)
    text = update.message.text.strip()

    # Step A: Capture Full Name Input
    if current_state == STATE_NAME:
        USER_DATA[user_id] = {"name": text}
        USER_STATE[user_id] = STATE_PHONE
        await update.message.reply_text("Great! Now please enter your **Phone Number** 📞:")
        return

    # Step B: Capture Phone Number Input
    elif current_state == STATE_PHONE:
        if user_id in USER_DATA:
            USER_DATA[user_id]["phone"] = text
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
            "🎓 Enjoy student-friendly competitive pricing in Adama\n\n"
            "📞 Call us anytime at: 0928854849\n\n"
            "📢 Announcement:\n"
            "We have started priority device delivery directly to ASTU Dorms!\n"
            "💰 Fast campus distribution guarantee!\n\n"
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
        
        # Pull registration variables from memory data backup, or fallback to webapp arguments
        saved_info = USER_DATA.get(user_id, {})
        name = saved_info.get("name", order_package.get("name", "Unknown Profile"))
        phone = saved_info.get("phone", order_package.get("phone", "No Phone Provided"))
        
        cart = order_package.get("cart", [])
        total = order_package.get("total", 0)
        
        user_meta = update.effective_user
        handle = f"@{user_meta.username}" if user_meta.username else "No Username"

        # Build clean string listing array items 
        items_ordered = []
        for item in cart:
            items_ordered.append(f"{item.get('name')} (Price: {item.get('price')} ETB)")
        order_summary_string = ", ".join(items_ordered)

        # EXACT INVOICE FORMAT MATCHING YOUR SYSTEM LOG
        receipt_template = f"""🚨 NEW ORDER
━━━━━━━━━━━━━━━
👤 Name: {name}
📞 Phone: {phone}
🆔 TG: {handle}
🍱 Order: {order_summary_string}
💰 Total: {total} ETB
━━━━━━━━━━━━━━━"""

        # Dispatches structured receipt block safely to Admin Chat Panel
        await context.bot.send_message(chat_id=ADMIN_ID, text=receipt_template)
        
        # Customer success response confirmation text
        await update.message.reply_text(
            f"🎉 Order received successfully, {name}!\n"
            f"Our team will process your order and contact you shortly."
        )

    except Exception as error:
        logger.error(f"Error compiling webapp data packet: {error}")

# ==========================================
# 3. RUN ENGINE LOOP DEFINITION
# ==========================================
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))
    # Handles interactive incoming chat setup answers text fields
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_registration_messages))
    
    print("🤖 Processing Loop Initialized. Bot running smoothly...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
