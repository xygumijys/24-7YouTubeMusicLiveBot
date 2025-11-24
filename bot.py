#!/usr/bin/env python3
"""
24/7 YouTube Music Live Bot
Main bot application for streaming music/video to YouTube Live 24/7
"""

import os
import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv

from stream_manager import StreamManager
from file_handler import FileHandler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global stream manager
stream_manager = StreamManager()
file_handler = FileHandler()


def is_admin(user_id: int) -> bool:
    """Check if user is an admin"""
    admin_ids = os.getenv('ADMIN_USER_IDS', '').split(',')
    return str(user_id) in admin_ids or not admin_ids


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    welcome_message = """
🎵 *24/7 YouTube Music Live Bot*

Welcome! I can stream your music/video to YouTube Live 24/7.

*Available Commands:*
/start - Show this message
/upload - Upload a video/audio file
/add_gdrive <link> - Add a Google Drive file
/stream - Start streaming to YouTube Live
/stop - Stop the current stream
/status - Check stream status
/list - List all uploaded files
/help - Get detailed help

*Features:*
✨ 24/7 Live streaming
✨ Free to run on cloud platforms
✨ Multi-stream support
✨ Google Drive integration
✨ Auto-loop your content

Send me a video or audio file to get started!
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_message = """
📖 *Detailed Help*

*Setup:*
1. Create a Telegram bot using @BotFather
2. Get your YouTube Live stream key from YouTube Studio
3. Configure environment variables
4. Deploy to Render, Koyeb, or Railway

*Commands:*

/upload - Upload files directly through Telegram
• Send video or audio files (up to 50MB)
• Supported formats: MP4, MKV, MP3, WAV

/add_gdrive <link> - Add files from Google Drive
• Share your file publicly or with service account
• Paste the Google Drive link

/stream - Start streaming
• Automatically loops your uploaded content
• Streams to YouTube Live 24/7
• Requires YouTube stream key in environment

/stop - Stop streaming
• Gracefully stops the current stream
• Can restart later with /stream

/status - Check stream status
• Shows if stream is active
• Displays current file being played
• Shows stream uptime

/list - List uploaded files
• Shows all files in your library
• Use to manage your content

*Multi-Stream Setup:*
Create different Telegram groups and add the bot to each group.
Each group can have its own independent stream.

*Tips:*
• Upload multiple files for variety
• Use high-quality videos for better streaming
• Monitor status regularly
• Keep your stream key secret
    """
    await update.message.reply_text(help_message, parse_mode='Markdown')


async def upload_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /upload command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⚠️ Only admins can upload files.")
        return
    
    await update.message.reply_text(
        "📤 Please send me a video or audio file to upload.\n"
        "Supported formats: MP4, MKV, MP3, WAV"
    )


async def add_gdrive_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /add_gdrive command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⚠️ Only admins can add files.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a Google Drive link.\n"
            "Usage: /add_gdrive <google_drive_link>"
        )
        return
    
    gdrive_link = context.args[0]
    await update.message.reply_text("⏳ Downloading from Google Drive...")
    
    try:
        file_path = await file_handler.download_from_gdrive(gdrive_link)
        chat_id = update.effective_chat.id
        stream_manager.add_file(chat_id, file_path)
        await update.message.reply_text(
            f"✅ File downloaded and added to library!\n"
            f"Use /stream to start streaming."
        )
    except Exception as e:
        logger.error(f"Error downloading from Google Drive: {e}")
        await update.message.reply_text(
            f"❌ Error downloading file: {str(e)}\n"
            "Make sure the file is publicly accessible."
        )


async def stream_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stream command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⚠️ Only admins can start streams.")
        return
    
    chat_id = update.effective_chat.id
    
    if stream_manager.is_streaming(chat_id):
        await update.message.reply_text("⚠️ Stream is already running!")
        return
    
    files = stream_manager.get_files(chat_id)
    if not files:
        await update.message.reply_text(
            "⚠️ No files uploaded yet!\n"
            "Please upload files first using /upload or /add_gdrive"
        )
        return
    
    await update.message.reply_text("🎬 Starting YouTube Live stream...")
    
    try:
        success = await stream_manager.start_stream(chat_id)
        if success:
            await update.message.reply_text(
                "✅ Stream started successfully!\n"
                f"📺 Streaming {len(files)} file(s) in loop.\n"
                "Use /status to check stream status."
            )
        else:
            await update.message.reply_text(
                "❌ Failed to start stream.\n"
                "Please check your YouTube stream key configuration."
            )
    except Exception as e:
        logger.error(f"Error starting stream: {e}")
        await update.message.reply_text(f"❌ Error starting stream: {str(e)}")


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stop command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⚠️ Only admins can stop streams.")
        return
    
    chat_id = update.effective_chat.id
    
    if not stream_manager.is_streaming(chat_id):
        await update.message.reply_text("⚠️ No stream is currently running.")
        return
    
    await update.message.reply_text("🛑 Stopping stream...")
    
    try:
        await stream_manager.stop_stream(chat_id)
        await update.message.reply_text("✅ Stream stopped successfully!")
    except Exception as e:
        logger.error(f"Error stopping stream: {e}")
        await update.message.reply_text(f"❌ Error stopping stream: {str(e)}")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command"""
    chat_id = update.effective_chat.id
    status = stream_manager.get_status(chat_id)
    
    if status['is_streaming']:
        uptime = status.get('uptime', 'Unknown')
        current_file = status.get('current_file', 'Unknown')
        await update.message.reply_text(
            f"📊 *Stream Status*\n\n"
            f"Status: 🟢 Active\n"
            f"Uptime: {uptime}\n"
            f"Current File: {current_file}\n"
            f"Total Files: {status.get('total_files', 0)}",
            parse_mode='Markdown'
        )
    else:
        file_count = len(stream_manager.get_files(chat_id))
        await update.message.reply_text(
            f"📊 *Stream Status*\n\n"
            f"Status: 🔴 Inactive\n"
            f"Uploaded Files: {file_count}\n"
            f"Use /stream to start streaming.",
            parse_mode='Markdown'
        )


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /list command"""
    chat_id = update.effective_chat.id
    files = stream_manager.get_files(chat_id)
    
    if not files:
        await update.message.reply_text(
            "📁 No files uploaded yet.\n"
            "Use /upload or /add_gdrive to add files."
        )
        return
    
    file_list = "\n".join([f"{i+1}. {os.path.basename(f)}" for i, f in enumerate(files)])
    await update.message.reply_text(
        f"📁 *Uploaded Files ({len(files)})*\n\n{file_list}",
        parse_mode='Markdown'
    )


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle file uploads"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⚠️ Only admins can upload files.")
        return
    
    message = update.message
    file = None
    file_name = None
    
    # Check for video or audio
    if message.video:
        file = message.video
        file_name = message.video.file_name or f"video_{message.video.file_id}.mp4"
    elif message.audio:
        file = message.audio
        file_name = message.audio.file_name or f"audio_{message.audio.file_id}.mp3"
    elif message.document:
        # Check if document is a video or audio file
        mime_type = message.document.mime_type or ""
        if mime_type.startswith(('video/', 'audio/')):
            file = message.document
            file_name = message.document.file_name or f"file_{message.document.file_id}"
        else:
            await update.message.reply_text(
                "⚠️ Unsupported file type.\n"
                "Please send video or audio files only."
            )
            return
    
    if not file:
        return
    
    await update.message.reply_text("⏳ Downloading file...")
    
    try:
        # Download file
        file_path = await file_handler.download_telegram_file(file, file_name, context.bot)
        
        # Add to stream manager
        chat_id = update.effective_chat.id
        stream_manager.add_file(chat_id, file_path)
        
        await update.message.reply_text(
            f"✅ File uploaded successfully!\n"
            f"📁 File: {file_name}\n"
            f"Use /stream to start streaming."
        )
    except Exception as e:
        logger.error(f"Error handling file upload: {e}")
        await update.message.reply_text(f"❌ Error uploading file: {str(e)}")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors"""
    logger.error(f"Exception while handling an update: {context.error}")


def main() -> None:
    """Start the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    # Create storage directory
    storage_path = os.getenv('STORAGE_PATH', './storage/')
    os.makedirs(storage_path, exist_ok=True)
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("upload", upload_command))
    application.add_handler(CommandHandler("add_gdrive", add_gdrive_command))
    application.add_handler(CommandHandler("stream", stream_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("list", list_command))
    
    # Add file handler
    application.add_handler(MessageHandler(
        filters.VIDEO | filters.AUDIO | filters.Document.ALL,
        handle_file
    ))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
