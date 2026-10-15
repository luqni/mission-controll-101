import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from orchestrator import run_mission_pipeline

# Konfigurasi Token & ID Pemilik
BOT_TOKEN = "MASUKKAN_BOT_TOKEN_DARI_BOTFATHER"
ADMIN_TELEGRAM_ID = 123456789  # Ganti dengan User ID Telegram Anda

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_TELEGRAM_ID:
        await update.message.reply_text("Akses ditolak.")
        return
    await update.message.reply_text(
        "🎛️ **Mission Control Online**\n\n"
        "Kirim instruksi tugas atau fitur baru. Tim developer virtual akan memprosesnya dari riset, koding, hingga audit QA."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_TELEGRAM_ID:
        return

    task_desc = update.message.text
    chat_id = update.effective_chat.id

    def notify(message):
        asyncio.run_coroutine_threadsafe(
            context.bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown"),
            context.application.loop
        )

    await update.message.reply_text("📋 Misi diterima. Meneruskan ke orkestrator...")

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, run_mission_pipeline, task_desc, notify)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
