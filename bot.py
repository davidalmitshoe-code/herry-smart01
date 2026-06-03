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

# ==========================
# CONFIGURATION
# ==========================

TOKEN = "8820217071:AAFnpv9DJnHUai2LlGQx86t8bb4sj3fVVuE"

ADMIN_ID = 998942116

WEBAPP_URL = "YOUR_RENDER_WEBAPP_URL"

NAME, PHONE, PLACE = range(3)

# ==========================
# START
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "📱👋 **Welcome to Herry Mobile & Electronics Shop!**\n\n"
        "To provide accurate delivery estimations, let's complete a quick setup profile.\n"
        "What is your **Full Name**?"
    )

    return NAME


# ==========================
# NAME
# ==========================

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["name"] = update.message.text

    await update.message.reply_text(
        "📞Thank you. Now, please enter your **Phone Number**:"
    )

    return PHONE


# ==========================
# PHONE
# ==========================

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["phone"] = update.message.text

    await update.message.reply_text(
        "📍 Perfect! Now Enter Delivery  Specific Place:"
    )

    return PLACE


# ==========================
# PLACE
# ==========================

async def get_place(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["place"] = update.message.text

    username = update.effective_user.username

    if username:
        context.user_data["username"] = username
    else:
        context.user_data["username"] = "No Username"

    # Send registration to admin
    registration_message = f"""
🆕 NEW CUSTOMER

👤 Name: {context.user_data['name']}

📞 Phone: {context.user_data['phone']}

📍 Place: {context.user_data['place']}

👤 Username: @{context.user_data['username']}
"""

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=registration_message
    )

    keyboard = [
        [
            InlineKeyboardButton(
                text="🛒 Open Shop",
                web_app=WebAppInfo(url=WEBAPP_URL)
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
# MINI APP ORDER RECEIVER
# ==========================

async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        import json

        data = update.effective_message.web_app_data.data

        order = json.loads(data)

        customer = update.effective_user

        products_text = ""

        for item in order["cart"]:
            products_text += (
                f"• {item['name']} - {item['price']} ETB\n"
            )

        message = f"""
🛍 NEW ORDER

👤 User: {customer.full_name}

📱 Username: @{customer.username}

📦 Products:
{products_text}

💰 Total Price:
{order['total']} ETB
"""

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=message
        )

        await update.message.reply_text(
            "✅ Order Sent Successfully!"
        )

    except Exception as e:

        print("ORDER ERROR:", e)

        await update.message.reply_text(
            "❌ Order Failed."
        )


# ==========================
# CANCEL
# ==========================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Registration cancelled."
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

    print("Bot Running...")

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
