import configparser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, Application, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters
from utils import test
from chatbot import OpenAIBot
from log import logger
from database import insert_video_data, get_meals_tags, get_info_with_tag, get_tv_review_names, write_tv_review, insert_review_data, read_tv_review_with_name

allowed_user_list = ["riverfjs", "victorwangkai", -1001643700527]
tt = OpenAIBot()
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
insert_video_data()  # prepare the video data
insert_review_data()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("你好, {}, 请选择左下角菜单开始使用！喵~".format(update.message.from_user["first_name"]))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Good day, {}!".format(context.args[0]))


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /chat is issued."""
    user = update.message.from_user
    chatID = update.message.chat.id
    if user["username"] in allowed_user_list or chatID in allowed_user_list:
        keyword = " ".join(context.args)
        if not keyword:
            await update.message.reply_text("请在命令后输入文字 /chat <keyword>，喵~")
        else:
            await update.message.reply_text(tt.reply(query=keyword, context={"user_id": user["username"], "type": "TEXT"}))
    else:
        await update.message.reply_text("对不起，不认识你！ 喵~ 不给用 喵~")


async def image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /image is issued."""

    user = update.message.from_user
    chatID = update.message.chat.id
    if user["username"] in allowed_user_list or chatID in allowed_user_list:
        keyword = " ".join(context.args)
        if not keyword:
            await update.message.reply_text("请在命令后输入文字 /image <keyword>，喵~")
        else:
            await update.message.reply_photo(tt.reply(query=keyword, context={"user_id": user["username"], "type": "IMAGE_CREATE"}))
    else:
        await update.message.reply_text("对不起，不认识你！ 喵~ 不给用 喵~")


async def ytb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /image is issued."""
    user = update.message.from_user
    chatID = update.message.chat.id
    if user["username"] in allowed_user_list or chatID in allowed_user_list:
        keyword = " ".join(context.args)
        if not keyword:
            await update.message.reply_text("请在命令后输入文字 /video <keyword>，喵~")
        else:
            await update.message.reply_text(test(keyword))
    else:
        await update.message.reply_text("对不起，不认识你！ 喵~ 不给用 喵~")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    # logger.warn(update.message.chat.id)
    # await update.message.reply_text(update.message.chat.id)
    await update.message.reply_text(update.message.chat)


async def cook(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send meals video to user."""
    user = update.message.from_user
    chatID = update.message.chat.id
    if user["username"] in allowed_user_list or chatID in allowed_user_list:
        keyword = " ".join(context.args)
        if not keyword:
            tags = get_meals_tags()
            await update.message.reply_text("请在命令后输入文字 /cook <keyword>，你可以选择："+tags+"喵~")
        else:
            data = get_info_with_tag(keyword)
            if data == "":
                tags = get_meals_tags()
                await update.message.reply_text("请在命令后输入文字 /cook <keyword>，你可以选择："+tags+"喵~")
            await update.message.reply_text(data)
    else:
        await update.message.reply_text("对不起，不认识你！ 喵~ 不给用 喵~")


async def read_tv_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send meals video to user."""
    user = update.message.from_user
    chatID = update.message.chat.id
    if user["username"] in allowed_user_list or chatID in allowed_user_list:
        keyword = " ".join(context.args)
        if not keyword:
            tags = get_tv_review_names()
            await update.message.reply_text("请在命令后输入文字 /tv-review <keyword>，你可以选择："+tags+"喵~")
        else:
            data = read_tv_review_with_name(keyword)
            if data == "":
                tags = get_tv_review_names()
                await update.message.reply_text("请在命令后输入文字 /tv-review <keyword>，你可以选择："+tags+"喵~")
            await update.message.reply_text(data)
    else:
        await update.message.reply_text("对不起，不认识你！ 喵~ 不给用 喵~")


async def write_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Store the user's TV review"""
    user = update.message.from_user
    chatID = update.message.chat.id
    if user["username"] in allowed_user_list or chatID in allowed_user_list:
        keyword = " ".join(context.args)
        if not keyword:
            await update.message.reply_text("请在命令后输入文字 /write-review <name> <review> 喵~")
        else:
            command = keyword.split(" ")
            await update.message.reply_text(write_tv_review(command[0], command[1]))
    else:
        await update.message.reply_text("对不起，不认识你！ 喵~ 不给用 喵~")

app = ApplicationBuilder().token(
    token=(config['TELEGRAM']['ACCESS_TOKEN'])).build()

app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("chat", chat))
app.add_handler(CommandHandler("image", image))
app.add_handler(CommandHandler("video", ytb))
app.add_handler(CommandHandler("cook", cook))
app.add_handler(CommandHandler("tv-review"), read_tv_review)
app.add_handler(CommandHandler("write-review"), write_review)


# app.add_handler(CommandHandler("add", add))

# app.add_handler(CallbackQueryHandler(button))
# app.add_handler(CommandHandler("startchat", start_chat))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.run_polling()
