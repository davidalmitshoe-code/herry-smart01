from telegram import (
    Update,
    WebAppInfo,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
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

# ==========================
# CONFIGURATION
# ==========================

TOKEN = "8820217071:AAGltetsRpmnq4OG_osBdHH5pcvL0EJNdG4"

ADMIN_ID = 998942116

WEBAPP_URL = "https://davidalmitshoe-code.github.io/herry-smart01/"

NAME, PHONE, PLACE = range(3)

# ==========================
# START
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "📱 Welcome to Herry Mobile & Electronics\n\n"
        "Please enter your Full Name:"
    )

    return NAME


# ==========================
# NAME
# ==========================

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["name"] = update.message.text.strip()

    await update.message.reply_text(
        "📞 Enter Phone Number:"
    )

    return PHONE


# ==========================
# PHONE
# ==========================

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["phone"] = update.message.text.strip()

    await update.message.reply_text(
        "📍 Enter Delivery Place:"
    )

    return PLACE


# ==========================
# PLACE
# ==========================

async def get_place(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["place"] = update.message.text.strip()

    username = update.effective_user.username or "No Username"

    context.user_data["username"] = username

    registration_message = f"""
🆕 NEW CUSTOMER

👤 Name: {context.user_data['name']}
📞 Phone: {context.user_data['phone']}
📍 Place: {context.user_data['place']}
📱 Username: @{username}
"""

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=registration_message
        )
    except Exception as e:
        print("ADMIN MESSAGE ERROR:", e)

    keyboard = [
        [
            InlineKeyboardButton(
                text="🛒 Open Shop",
                web_app=WebAppInfo(
                    url=WEBAPP_URL
                )
            )
        ]
    ]

    await update.message.reply_text(
        "✅ Registration Completed!\n\n"
        "Click the button below to open the shop.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return ConversationHandler.END


# ==========================
# RECEIVE MINI APP ORDER
# ==========================

async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        raw_data = update.effective_message.web_app_data.data

        print("RAW DATA:", raw_data)

        order = json.loads(raw_data)

        customer = update.effective_user

        username = customer.username or "No Username"

        cart = order.get("cart", [])

        total = order.get("total", 0)

        products_text = ""

        for item in cart:

            name = item.get("name", "Unknown Product")
            price = item.get("price", 0)

            products_text += f"• {name} - {price} ETB\n"

        message = f"""
🛍 NEW ORDER

👤 Customer: {customer.full_name}
📱 Username: @{username}

📦 Products:
{products_text}

💰 Total: {total} ETB
"""

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=message
        )

        await update.message.reply_text(
            "✅ Order Sent Successfully!"
        )

    except Exception as e:

        print("WEBAPP ERROR:", e)

        await update.message.reply_text(
            "❌ Order Failed."
        )


# ==========================
# CANCEL
# ==========================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "❌ Registration Cancelled."
    )

    return ConversationHandler.END


# ==========================
# MAIN
# ==========================

def main():

    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(

        entry_points=[
            CommandHandler("start", start)
        ],

        states={

            NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_name
                )
            ],

            PHONE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_phone
                )
            ],

            PLACE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_place
                )
            ]
        },

        fallbacks=[
            CommandHandler("cancel", cancel)
        ]
    )

    app.add_handler(conv_handler)

    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.WEB_APP_DATA,
            webapp_data
        )
    )

    print("✅ Bot Running...")

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
