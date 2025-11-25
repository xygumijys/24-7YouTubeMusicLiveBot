#!/usr/bin/env python3
"""
24/7 YouTube Music Live Bot
Main bot application for streaming music/video to YouTube Live 24/7
"""

import os
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

*Stream Key Commands:*
/setkey <key> - Set YouTube stream key
/setrtmp <url> - Set custom RTMP URL
/showkey - Show current stream key (masked)

*Live Control Commands:*
/switch <number> - Switch to specific file
/next - Skip to next file
/prev - Go to previous file
/nowplaying - Show current playing file
/remove <number> - Remove file from playlist

*Features:*
✨ 24/7 Live streaming
✨ Free to run on cloud platforms
✨ Multi-stream support
✨ Live video/audio switching
✨ Per-chat stream key support
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
3. Set your stream key using /setkey command
4. Upload files and start streaming!

*Basic Commands:*

/upload - Upload files directly through Telegram
• Send video or audio files (up to 50MB)
• Supported formats: MP4, MKV, MP3, WAV

/add_gdrive <link> - Add files from Google Drive
• Share your file publicly or with service account
• Paste the Google Drive link

/stream - Start streaming
• Automatically loops your uploaded content
• Streams to YouTube Live 24/7

/stop - Stop streaming
• Gracefully stops the current stream
• Can restart later with /stream

/status - Check stream status
• Shows if stream is active
• Displays current file being played

/list - List uploaded files
• Shows all files in your library

*Stream Key Commands:*

/setkey <key> - Set YouTube stream key
• Each chat can have its own stream key
• Falls back to environment variable if not set

/setrtmp <url> - Set custom RTMP URL
• Default: rtmp://a.rtmp.youtube.com/live2/
• Use for custom streaming destinations

/showkey - Show current stream key
• Displays masked key for security

*Live Control (StreamYard-like features):*

/switch <number> - Switch to specific file
• Instantly switch during live stream
• Use /list to see file numbers

/next - Skip to next file
• Jump to next file in playlist

/prev - Go to previous file
• Jump to previous file in playlist

/nowplaying - Show current file
• Displays currently streaming file

/remove <number> - Remove file
• Remove a file from playlist

*Multi-Stream Setup:*
Create different Telegram groups and add the bot.
Each group has its own stream key and playlist!

*Tips:*
• Set stream key via bot for easier management
• Use /switch for seamless content changes
• Monitor with /status regularly
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
            "✅ File downloaded and added to library!\n"
            "Use /stream to start streaming."
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
    
    # Check if stream key is configured
    stream_key = stream_manager.get_stream_key(chat_id)
    if not stream_key:
        await update.message.reply_text(
            "⚠️ No stream key configured!\n\n"
            "Use /setkey <your_stream_key> to set your YouTube stream key.\n"
            "Get it from YouTube Studio → Go Live → Stream settings"
        )
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
            current_file = os.path.basename(files[stream_manager.get_current_file_index(chat_id)])
            await update.message.reply_text(
                "✅ Stream started successfully!\n"
                f"📺 Streaming {len(files)} file(s) in loop.\n"
                f"🎵 Now playing: {current_file}\n\n"
                "Use /status to check stream status.\n"
                "Use /switch, /next, /prev to control playback."
            )
        else:
            await update.message.reply_text(
                "❌ Failed to start stream.\n"
                "Please check your YouTube stream key with /showkey"
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


async def setkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /setkey command - Set YouTube stream key"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⚠️ Only admins can set stream key.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide your YouTube stream key.\n"
            "Usage: /setkey <your_stream_key>\n\n"
            "Get your stream key from YouTube Studio → Go Live → Stream settings"
        )
        return
    
    stream_key = context.args[0]
    chat_id = update.effective_chat.id
    
    stream_manager.set_stream_key(chat_id, stream_key)
    
    # Mask the key for display
    masked_key = stream_key[:4] + "****" + stream_key[-4:] if len(stream_key) > 8 else "****"
    
    await update.message.reply_text(
        f"✅ Stream key set successfully!\n"
        f"🔑 Key: {masked_key}\n\n"
        f"Use /stream to start streaming to YouTube Live."
    )


async def setrtmp_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /setrtmp command - Set custom RTMP URL"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⚠️ Only admins can set RTMP URL.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide the RTMP URL.\n"
            "Usage: /setrtmp <rtmp_url>\n\n"
            "Default: rtmp://a.rtmp.youtube.com/live2/\n"
            "Use /setrtmp default to reset to YouTube default."
        )
        return
    
    rtmp_url = context.args[0]
    chat_id = update.effective_chat.id
    
    if rtmp_url.lower() == 'default':
        stream_manager.rtmp_urls.pop(chat_id, None)
        await update.message.reply_text(
            "✅ RTMP URL reset to default!\n"
            "📡 URL: rtmp://a.rtmp.youtube.com/live2/"
        )
    else:
        stream_manager.set_rtmp_url(chat_id, rtmp_url)
        await update.message.reply_text(
            f"✅ RTMP URL set successfully!\n"
            f"📡 URL: {rtmp_url}"
        )


async def showkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /showkey command - Show current stream key (masked)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⚠️ Only admins can view stream key.")
        return
    
    chat_id = update.effective_chat.id
    stream_key = stream_manager.get_stream_key(chat_id)
    rtmp_url = stream_manager.get_rtmp_url(chat_id)
    
    if stream_key:
        # Mask the key for security
        masked_key = stream_key[:4] + "****" + stream_key[-4:] if len(stream_key) > 8 else "****"
        source = "Per-chat key" if chat_id in stream_manager.stream_keys else "Environment variable"
        await update.message.reply_text(
            f"🔑 *Stream Configuration*\n\n"
            f"Stream Key: `{masked_key}`\n"
            f"Source: {source}\n"
            f"RTMP URL: `{rtmp_url}`",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "⚠️ No stream key configured!\n"
            "Use /setkey <your_key> to set your YouTube stream key."
        )


async def switch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /switch command - Switch to specific file during live stream"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⚠️ Only admins can switch files.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide the file number.\n"
            "Usage: /switch <number>\n\n"
            "Use /list to see file numbers."
        )
        return
    
    try:
        file_index = int(context.args[0]) - 1  # Convert to 0-based index
    except ValueError:
        await update.message.reply_text("⚠️ Please provide a valid number.")
        return
    
    chat_id = update.effective_chat.id
    files = stream_manager.get_files(chat_id)
    
    if not files:
        await update.message.reply_text("⚠️ No files uploaded. Use /upload first.")
        return
    
    if not (0 <= file_index < len(files)):
        await update.message.reply_text(
            f"⚠️ Invalid file number. Choose between 1 and {len(files)}.\n"
            "Use /list to see available files."
        )
        return
    
    file_name = os.path.basename(files[file_index])
    
    if stream_manager.is_streaming(chat_id):
        await update.message.reply_text(f"🔄 Switching to: {file_name}...")
        success = await stream_manager.switch_to_file(chat_id, file_index)
        if success:
            await update.message.reply_text(
                f"✅ Now playing: {file_name}\n"
                f"Stream continues with new content!"
            )
        else:
            await update.message.reply_text("❌ Failed to switch file.")
    else:
        stream_manager.set_current_file_index(chat_id, file_index)
        await update.message.reply_text(
            f"✅ Starting file set to: {file_name}\n"
            f"Use /stream to start streaming."
        )


async def next_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /next command - Skip to next file"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⚠️ Only admins can control playback.")
        return
    
    chat_id = update.effective_chat.id
    files = stream_manager.get_files(chat_id)
    
    if not files:
        await update.message.reply_text("⚠️ No files uploaded. Use /upload first.")
        return
    
    if len(files) < 2:
        await update.message.reply_text("⚠️ Need at least 2 files to skip.")
        return
    
    current_index = stream_manager.get_current_file_index(chat_id)
    next_index = (current_index + 1) % len(files)
    next_file = os.path.basename(files[next_index])
    
    if stream_manager.is_streaming(chat_id):
        await update.message.reply_text(f"⏭️ Skipping to next: {next_file}...")
        success = await stream_manager.next_file(chat_id)
        if success:
            await update.message.reply_text(f"✅ Now playing: {next_file}")
        else:
            await update.message.reply_text("❌ Failed to skip to next file.")
    else:
        stream_manager.set_current_file_index(chat_id, next_index)
        await update.message.reply_text(
            f"✅ Next file queued: {next_file}\n"
            f"Use /stream to start streaming."
        )


async def prev_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /prev command - Go to previous file"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⚠️ Only admins can control playback.")
        return
    
    chat_id = update.effective_chat.id
    files = stream_manager.get_files(chat_id)
    
    if not files:
        await update.message.reply_text("⚠️ No files uploaded. Use /upload first.")
        return
    
    if len(files) < 2:
        await update.message.reply_text("⚠️ Need at least 2 files to go back.")
        return
    
    current_index = stream_manager.get_current_file_index(chat_id)
    prev_index = (current_index - 1) % len(files)
    prev_file = os.path.basename(files[prev_index])
    
    if stream_manager.is_streaming(chat_id):
        await update.message.reply_text(f"⏮️ Going back to: {prev_file}...")
        success = await stream_manager.prev_file(chat_id)
        if success:
            await update.message.reply_text(f"✅ Now playing: {prev_file}")
        else:
            await update.message.reply_text("❌ Failed to go to previous file.")
    else:
        stream_manager.set_current_file_index(chat_id, prev_index)
        await update.message.reply_text(
            f"✅ Previous file queued: {prev_file}\n"
            f"Use /stream to start streaming."
        )


async def nowplaying_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /nowplaying command - Show current playing file"""
    chat_id = update.effective_chat.id
    files = stream_manager.get_files(chat_id)
    
    if not files:
        await update.message.reply_text("⚠️ No files uploaded yet.")
        return
    
    current_index = stream_manager.get_current_file_index(chat_id)
    current_file = os.path.basename(files[current_index])
    
    status = "🟢 Streaming" if stream_manager.is_streaming(chat_id) else "🔴 Not streaming"
    
    await update.message.reply_text(
        f"🎵 *Now Playing*\n\n"
        f"Status: {status}\n"
        f"File: {current_file}\n"
        f"Track: {current_index + 1}/{len(files)}",
        parse_mode='Markdown'
    )


async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /remove command - Remove file from playlist"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⚠️ Only admins can remove files.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide the file number to remove.\n"
            "Usage: /remove <number>\n\n"
            "Use /list to see file numbers."
        )
        return
    
    try:
        file_index = int(context.args[0]) - 1  # Convert to 0-based index
    except ValueError:
        await update.message.reply_text("⚠️ Please provide a valid number.")
        return
    
    chat_id = update.effective_chat.id
    files = stream_manager.get_files(chat_id)
    
    if not files:
        await update.message.reply_text("⚠️ No files to remove.")
        return
    
    if not (0 <= file_index < len(files)):
        await update.message.reply_text(
            f"⚠️ Invalid file number. Choose between 1 and {len(files)}."
        )
        return
    
    # Don't allow removal during streaming
    if stream_manager.is_streaming(chat_id):
        await update.message.reply_text(
            "⚠️ Cannot remove files during active stream.\n"
            "Use /stop first, then remove files."
        )
        return
    
    removed_file = stream_manager.remove_file(chat_id, file_index)
    if removed_file:
        await update.message.reply_text(
            f"✅ Removed: {os.path.basename(removed_file)}\n"
            f"Remaining files: {len(stream_manager.get_files(chat_id))}"
        )
    else:
        await update.message.reply_text("❌ Failed to remove file.")


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
    
    # Stream key and RTMP commands
    application.add_handler(CommandHandler("setkey", setkey_command))
    application.add_handler(CommandHandler("setrtmp", setrtmp_command))
    application.add_handler(CommandHandler("showkey", showkey_command))
    
    # Live control commands (StreamYard-like features)
    application.add_handler(CommandHandler("switch", switch_command))
    application.add_handler(CommandHandler("next", next_command))
    application.add_handler(CommandHandler("prev", prev_command))
    application.add_handler(CommandHandler("nowplaying", nowplaying_command))
    application.add_handler(CommandHandler("remove", remove_command))
    
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
