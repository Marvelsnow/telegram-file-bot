from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from flask import Flask, send_from_directory
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
UPLOAD_FOLDER = "static"
DOMAIN = os.getenv("DOMAIN")

flask_app = Flask(__name__)
flask_app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@flask_app.route("/static/<filename>")
def serve_file(filename):
    return send_from_directory(flask_app.config["UPLOAD_FOLDER"], filename)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or update.message.video or update.message.audio
    if not file:
        await update.message.reply_text("Send a file!")
        return

    tg_file = await file.get_file()
    file_path = os.path.join(UPLOAD_FOLDER, file.file_name)
    await tg_file.download_to_drive(file_path)

    link = f"{DOMAIN}/static/{file.file_name}"
    await update.message.reply_text(f"Here's your link:\n{link}")

def start_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.Document.ALL | filters.Video.ALL | filters.Audio.ALL, handle_file))
    app.run_polling()

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    import threading
    threading.Thread(target=flask_app.run, kwargs={"host": "0.0.0.0", "port": 10000}).start()
    start_bot()
