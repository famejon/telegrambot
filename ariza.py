import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
import openpyxl
import os

# --- Sozlamalar ---
FILE_NAME = "nomzodlar.xlsx"
ADMIN_LINK = "https://t.me/famejon"   # <-- bu yerda o'zingizning Telegram username havolangizni yozing
SITE_LINK = "https://quvasoyim.pythonanywhere.com/vote"  # <-- bu yerda o'z saytingiz havolasini yozing

# Fayl mavjud bo‘lmasa, yangisini yaratamiz
if not os.path.exists(FILE_NAME):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Ism Familiya", "Sinf", "Yo‘nalish", "Taklif 1", "Taklif 2", "Taklif 3"])
    wb.save(FILE_NAME)

# Logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Holatlar
NAME, CLASS, DIRECTION, GOAL1, GOAL2, GOAL3 = range(6)

# Tugmalar
DIRECTIONS = [
    ["Maktab Prezidenti"],
    ["Ilm-fan sardori"],
    ["Ijod va madaniyat sardori"],
    ["Sport sardori"],
    ["Axborot texnologiyalari va media sardori"],
    ["Ekologiya va atrof-muhit sardori"],
    ["Ijtimoiy hayot sardori"]
]

HELP_BUTTON = ["🆘 Yordam"]

def keyboard_with_help(extra_rows=None):
    keyboard = []
    if extra_rows:
        keyboard.extend(extra_rows)
    keyboard.append(HELP_BUTTON)
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

# --- Boshlanish ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! 😊\nIltimos, ism va familiyangizni kiriting:",
        reply_markup=keyboard_with_help()
    )
    return NAME

# --- Yordam tugmasi ---
async def help_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🧑‍💻 Agar sizda muammo bo‘lsa, shu havola orqali bog‘laning:\n👉 {ADMIN_LINK}"
    )

# --- Ma'lumot to‘plash ---
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🆘 Yordam":
        return await help_button(update, context)
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Ajoyib! Endi sinfingizni kiriting (masalan: 10-A):",
                                    reply_markup=keyboard_with_help())
    return CLASS

async def get_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🆘 Yordam":
        return await help_button(update, context)
    context.user_data["class"] = update.message.text
    await update.message.reply_text(
        "Endi quyidagi yo‘nalishlardan birini tanlang 👇",
        reply_markup=keyboard_with_help(DIRECTIONS)
    )
    return DIRECTION

async def get_direction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🆘 Yordam":
        return await help_button(update, context)
    context.user_data["direction"] = update.message.text
    await update.message.reply_text("Endi 1-taklif yoki maqsadingizni yozing:",
                                    reply_markup=keyboard_with_help())
    return GOAL1

async def get_goal1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🆘 Yordam":
        return await help_button(update, context)
    context.user_data["goal1"] = update.message.text
    await update.message.reply_text("Yaxshi! Endi 2-taklif yoki maqsadingizni yozing:",
                                    reply_markup=keyboard_with_help())
    return GOAL2

async def get_goal2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🆘 Yordam":
        return await help_button(update, context)
    context.user_data["goal2"] = update.message.text
    await update.message.reply_text("Zo‘r! Endi 3-taklif yoki maqsadingizni yozing:",
                                    reply_markup=keyboard_with_help())
    return GOAL3

async def get_goal3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🆘 Yordam":
        return await help_button(update, context)
    context.user_data["goal3"] = update.message.text

    # Excelga yozish
    wb = openpyxl.load_workbook(FILE_NAME)
    ws = wb.active
    ws.append([
        context.user_data["name"],
        context.user_data["class"],
        context.user_data["direction"],
        context.user_data["goal1"],
        context.user_data["goal2"],
        context.user_data["goal3"]
    ])
    wb.save(FILE_NAME)

    # ✅ Tugmalar: yana qo‘shish va saytda ovoz berish
    buttons = [
        [InlineKeyboardButton("🔁 Yana nomzod qo‘shish", callback_data="restart")],
        [InlineKeyboardButton("🌐 Ovoz berish", web_app=WebAppInfo(url=SITE_LINK))]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "✅ Ma'lumotlaringiz saqlandi!\nQuyidagilardan birini tanlang:",
        reply_markup=reply_markup
    )

    return ConversationHandler.END

# --- Inline tugma hodisalari ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "restart":
        await query.message.reply_text("Yangi nomzod uchun ism va familiyangizni kiriting:")
        return NAME

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi. /start buyrug‘i bilan qayta boshlashingiz mumkin.")
    return ConversationHandler.END

def main():
    TOKEN = "8320383161:AAEElu2v9RAvWQE7Rj81atNvbfEdcpYlR8w"  # <-- bu yerga tokenni yoz
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CLASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_class)],
            DIRECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_direction)],
            GOAL1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal1)],
            GOAL2: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal2)],
            GOAL3: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal3)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.COMMAND, cancel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, help_button))
    app.add_handler(MessageHandler(filters.ALL, help_button))
    app.add_handler(MessageHandler(filters.StatusUpdate, help_button))
    app.add_handler(MessageHandler(filters.TEXT, help_button))
    app.add_handler(MessageHandler(filters.Regex("🆘 Yordam"), help_button))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🆘 Yordam"), help_button))

    # Inline tugma handler
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("Yana nomzod qo‘shish"), start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("Ovoz berish"), help_button))
    app.add_handler(MessageHandler(filters.COMMAND, cancel))

    app.add_handler(MessageHandler(filters.StatusUpdate, help_button))
    app.add_handler(MessageHandler(filters.ALL, help_button))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, help_button))
    app.add_handler(MessageHandler(filters.Regex("🆘 Yordam"), help_button))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🆘 Yordam"), help_button))
    app.add_handler(MessageHandler(filters.COMMAND, cancel))

    app.add_handler(MessageHandler(filters.ALL, help_button))
    app.add_handler(MessageHandler(filters.StatusUpdate, help_button))
    app.add_handler(MessageHandler(filters.Regex("Yana nomzod qo‘shish"), start))
    app.add_handler(MessageHandler(filters.Regex("Ovoz berish"), help_button))

    app.add_handler(MessageHandler(filters.ALL, help_button))
    app.add_handler(MessageHandler(filters.TEXT, help_button))

    # Inline callback tugmalar
    app.add_handler(MessageHandler(filters.ALL, help_button))
    app.add_handler(MessageHandler(filters.Regex("Yana nomzod qo‘shish"), start))

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("Ovoz berish"), help_button))
    app.add_handler(MessageHandler(filters.Regex("🆘 Yordam"), help_button))
    app.add_handler(MessageHandler(filters.COMMAND, cancel))
    app.add_handler(MessageHandler(filters.TEXT, help_button))

    # Callback query handler
    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
