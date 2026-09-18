import os
import json
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

DATA_FILE = "files.json"


def load_files():
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_files(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "👋 Welcome to PY MULTIVERSE STORE!\n\n"
            "Send me a file to generate its link."
        )
        return

    file_key = context.args[0]
    files = load_files()

    if file_key not in files:
        await update.message.reply_text("❌ File not found.")
        return

    file_data = files[file_key]

    await update.message.reply_document(
        document=file_data["file_id"],
        caption=file_data.get("caption", "")
    )


async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message.document:
        return

    file_id = message.document.file_id
    file_name = message.document.file_name or "File"

    files = load_files()

    file_key = str(message.message_id)

    files[file_key] = {
        "file_id": file_id,
        "caption": f"📄 {file_name}"
    }

    save_files(files)

    me = await context.bot.get_me()

    link = f"https://t.me/{me.username}?start={file_key}"

    await message.reply_text(
        f"✅ File saved!\n\n"
        f"🔗 Your file link:\n{link}\n\n"
        f"👉 Put this link into Vplink."
    )


async def health(update, context):
    return "OK"


def main():
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError("BOT_TOKEN is missing")

    port = int(os.getenv("PORT", "10000"))
    render_url = os.getenv("RENDER_EXTERNAL_URL")

    if not render_url:
        raise RuntimeError("RENDER_EXTERNAL_URL is missing")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.Document.ALL, receive_file)
    )

    webhook_url = f"{render_url}/{token}"

    print("PY MULTIVERSE STORE starting...")
    print("Webhook URL:", webhook_url)

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=token,
        webhook_url=webhook_url,
    )


if __name__ == "__main__":
    main()
