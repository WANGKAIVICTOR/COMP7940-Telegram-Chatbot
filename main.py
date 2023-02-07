import configparser
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, Application, CommandHandler, ContextTypes, MessageHandler, filters

# def openDB():
#     conn = sqlite3.connect(r"D:\Files\CODE\Go\laqingdan\database.db")       #建立database.db数据库连接
#     cursor = conn.cursor()
#     return conn, cursor
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

app = ApplicationBuilder().token(token=(config['TELEGRAM']['ACCESS_TOKEN'])).build()

app.add_handler(CommandHandler("hello", echo))
# app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))

app.run_polling()