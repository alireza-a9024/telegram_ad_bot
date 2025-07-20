import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from keep_alive import keep_alive  # Keeps bot online

# 🔑 Replace with your actual bot token
TOKEN = "#################################"
ADMIN_ID = 176306979  # Replace with your Telegram user ID

ads_waiting_approval = {}

# ✅ Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

# 📌 Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send an ad using this format:\n\n"
                                    "Title: Example Product\n"
                                    "Description: A great item for sale\n"
                                    "Price: $100\n"
                                    "Contact: @alireza_a9024")

# 📌 Handle Incoming Ads
async def handle_ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    ad_text = update.message.text
    ad_id = update.message.message_id  # Unique ID for the ad

    # ✅ Check if the format is correct
    if "Title:" in ad_text and "Description:" in ad_text and "Price:" in ad_text and "Contact:" in ad_text:
        # Store the ad for approval
        ads_waiting_approval[ad_id] = (user.id, ad_text)

        # Send to Admin for Approval
        keyboard = [
            [InlineKeyboardButton("✅ Approve", callback_data=f"approve_{ad_id}")],
            [InlineKeyboardButton("❌ Reject", callback_data=f"reject_{ad_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"New Ad Submission:\n\n{ad_text}",
            reply_markup=reply_markup
        )
        await update.message.reply_text("✅ Your ad has been sent for approval.")
    else:
        await update.message.reply_text("❌ Incorrect format! Please follow this structure:\n\n"
                                        "Title: Example\nDescription: Nice item\nPrice: $100\nContact: @yourusername")

# 📌 Admin Approval/Reject
async def approve_reject_ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    action, ad_id = query.data.split("_")

    if int(ad_id) in ads_waiting_approval:
        user_id, ad_text = ads_waiting_approval.pop(int(ad_id))

        if action == "approve":
            # Forward the ad to the channel or group (replace CHAT_ID)
            CHAT_ID = -1002559896251  # Replace with your group/channel ID
            await context.bot.send_message(chat_id=CHAT_ID, text=f"📢 **New Ad:**\n\n{ad_text}")
            await query.edit_message_text("✅ Ad Approved and Posted!")
        else:
            await context.bot.send_message(chat_id=user_id, text="❌ Your ad was rejected.")
            await query.edit_message_text("❌ Ad Rejected!")

# 📌 Main Function
def main():
    keep_alive()  # Keep the bot running 24/7
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ad))
    app.add_handler(CallbackQueryHandler(approve_reject_ad))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
