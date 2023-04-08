import os
import logging
import configparser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters)
from utils import ytb_search
from chatbot import OpenAIBot
# from log import logger
from database import (
    insert_video_data,
    get_meals_tags,
    get_info_with_tag,
    get_tv_review_names,
    write_tv_review,
    insert_review_data,
    read_tv_review_with_name)

allowed_user_list = ["riverfjs", "victorwangkai", -1001643700527]
tt = OpenAIBot()
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
insert_video_data()  # prepare the video data
insert_review_data()

# Enable logging

logging.basicConfig(
    format="[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s", level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
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


async def video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /image is issued."""
    user = update.message.from_user
    chatID = update.message.chat.id
    logger.info("User %s started the video search.", user.first_name)
    if user["username"] in allowed_user_list or chatID in allowed_user_list:
        keyword = " ".join(context.args)
        if not keyword:
            await update.message.reply_text("请在命令后输入文字 /video <keyword>，喵~")
        else:
            ret_dict = ytb_search(keyword)
            if ret_dict == "换个关键词吧！":
                await update.message.reply_text("换个关键词吧！")
                return
            # print(ret_list)
            keyboard = [[InlineKeyboardButton(
                "{}".format(idx+1), callback_data="{}".format(ret)) for idx, ret in enumerate(ret_dict.values())]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            reply_text = ""
            for idx, title in enumerate((ret_dict.keys())):
                reply_text += "{}. {}\n".format(idx+1, title)
            await update.message.reply_text(reply_text+"\nClick the number below👇", reply_markup=reply_markup)
    else:
        await update.message.reply_text("对不起，不认识你！ 喵~ 不给用 喵~")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    if query.data == "end the query":
        await query.answer()
        await query.delete_message()
    else:
        await query.answer()
        keyboard = [
            [
                InlineKeyboardButton("❌ CLOSE", callback_data="end the query"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(query.data, reply_markup=reply_markup)


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
            else:
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
            await update.message.reply_text("请在命令后输入文字 /readreview <keyword>，你可以选择："+tags+"喵~")
        else:
            data = read_tv_review_with_name(keyword)
            if data == "":
                tags = get_tv_review_names()
                await update.message.reply_text("请在命令后输入文字 /readreview <keyword>，你可以选择："+tags+"喵~")
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
            await update.message.reply_text("请在命令后输入文字 /writereview <name> <review> 喵~")
        else:
            command = keyword.split(" ")
            await update.message.reply_text(write_tv_review(command[0], command[1]))
    else:
        await update.message.reply_text("对不起，不认识你！ 喵~ 不给用 喵~")

if os.getenv('AM_I_IN_A_DOCKER_CONTAINER'):
    app = ApplicationBuilder().token(
        token=(os.getenv('ACCESS_TOKEN'))).build()
else:
    app = ApplicationBuilder().token(
        token=(config['TELEGRAM']['ACCESS_TOKEN'])).build()

app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("chat", chat))
app.add_handler(CommandHandler("image", image))

app.add_handler(CommandHandler("video", video))
app.add_handler(CallbackQueryHandler(button))

app.add_handler(CommandHandler("cook", cook))
app.add_handler(CommandHandler("readreview", read_tv_review))
app.add_handler(CommandHandler("writereview", write_review))


# app.add_handler(CommandHandler("add", add))

# app.add_handler(CallbackQueryHandler(button))
# app.add_handler(CommandHandler("startchat", start_chat))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.run_polling()
