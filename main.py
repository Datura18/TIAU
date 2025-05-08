import asyncio
import logging
import schedule
import threading
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

TOKEN = "8045180400:AAFfswAfYIj6PRSUuJRiyShGpmvwCJa4Sng"
CHANNEL_ID = "@tabriz_iau"

logging.basicConfig(level=logging.INFO)
reminder_status = {}

phonebook = {
    "دانشکده مولتی مدیا": {
        "ریاست": "04135412134 داخلی 591",
        "معاونت": "04135412133  ",
        "دفتر دانشکده": "04135412134 داخلی 591",
    },
    "دانشکده معماری و شهرسازی": {
        "ریاست": "04135539208 داخلی 202",
        "کارگاه": "04135539200 داخلی 203",
    },
    "دانشکده هنر های صناعی": {
        "دفتر": "04135419966 داخلی 505"
    },
    "آموزش کل": {
        "کارشناسی": "04135419710 داخلی 501",
        "کارشناسی ارشد": "04135419710 داخلی 502"
    }
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    reminder_status[user.id] = True
    main_menu = [["اخبار مهم", "دفترچه تلفن", "یادآور رزرو غذا"]]
    await update.message.reply_text(
        f"سلام {user.first_name}! به ربات خوش اومدی.",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("گزینه مورد نظر خود را انتخاب کنید..")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.chat_id

    if text == "اخبار مهم":
        chat = await context.bot.get_chat(CHANNEL_ID)
        pinned = chat.pinned_message
        if pinned:
            await context.bot.forward_message(chat_id=user_id,
                                              from_chat_id=CHANNEL_ID,
                                              message_id=pinned.message_id)
        else:
            await update.message.reply_text("هیچ خبر مهمی نیست.")
    elif text == "دفترچه تلفن":
        keyboard = [[
            InlineKeyboardButton(faculty, callback_data=f"faculty_{faculty}")
        ] for faculty in phonebook]
        keyboard.append(
            [InlineKeyboardButton("صفحه اصلی", callback_data="main_menu")])
        await update.message.reply_text(
            "دانشکده مورد نظر را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(keyboard))
    elif text == "یادآور رزرو غذا":
        keyboard = [[
            InlineKeyboardButton("فعال‌سازی", callback_data="enable_reminder")
        ],
                    [
                        InlineKeyboardButton("غیرفعال‌سازی",
                                             callback_data="disable_reminder")
                    ],
                    [
                        InlineKeyboardButton("صفحه اصلی",
                                             callback_data="main_menu")
                    ]]
        await update.message.reply_text(
            "چهارشنبه‌ها ساعت 21", reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("faculty_"):
        faculty = data.replace("faculty_", "")
        if faculty in phonebook:
            items = phonebook[faculty]
            keyboard = [[
                InlineKeyboardButton(title,
                                     callback_data=f"item_{faculty}_{title}")
            ] for title in items]
            keyboard.append([
                InlineKeyboardButton("برگشت",
                                     callback_data="back_to_faculties")
            ])
            await query.edit_message_text(
                f"{faculty} - بخش مورد نظر را انتخاب کنید:",
                reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("item_"):
        parts = data.split("_")
        faculty = parts[1]
        title = "_".join(parts[2:])
        number = phonebook.get(faculty, {}).get(title, "یافت نشد.")
        keyboard = [[
            InlineKeyboardButton("برگشت", callback_data=f"faculty_{faculty}")
        ]]
        await query.edit_message_text(
            f"{faculty} - {title}:\n{number}",
            reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "back_to_faculties":
        keyboard = [[
            InlineKeyboardButton(faculty, callback_data=f"faculty_{faculty}")
        ] for faculty in phonebook]
        keyboard.append(
            [InlineKeyboardButton("صفحه اصلی", callback_data="main_menu")])
        await query.edit_message_text(
            "دانشکده مورد نظر را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "enable_reminder":
        reminder_status[user_id] = True
        await query.edit_message_text("یادآور فعال شد.")

    elif data == "disable_reminder":
        reminder_status[user_id] = False
        await query.edit_message_text("یادآور غیرفعال شد.")

    elif data == "main_menu":
        menu = [["اخبار مهم", "دفترچه تلفن", "یادآور رزرو غذا"]]
        await context.bot.send_message(chat_id=user_id,
                                       text="بازگشت به منوی اصلی.",
                                       reply_markup=ReplyKeyboardMarkup(
                                           menu, resize_keyboard=True))


async def scheduled_task(app: Application):
    for user_id, enabled in reminder_status.items():
        if enabled:
            try:
                await app.bot.send_message(chat_id=user_id,
                                           text="یادت نره غذاتو رزرو کنی!")
            except Exception as e:
                print(f"Error sending to {user_id}: {e}")


def run_scheduler(app: Application):
    schedule.every().wednesday.at("21:00").do(
        lambda: asyncio.run(scheduled_task(app)))
    while True:
        schedule.run_pending()
        time.sleep(30)


async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(handle_callback))

    threading.Thread(target=run_scheduler, args=(app, ), daemon=True).start()

    print("ربات در حال اجراست...")
    await app.run_polling()


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.run(main())

from flask import Flask
from threading import Thread

app_web = Flask('')


@app_web.route('/')
def home():
    return "I'm alive!"


def run():
    app_web.run(host='0.0.0.0', port=8080)


Thread(target=run).start()
