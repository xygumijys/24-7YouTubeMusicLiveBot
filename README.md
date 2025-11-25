# 🎵 24/7 YouTube Music Live Bot

A powerful, **Free-to-Run** Telegram bot that streams your music/video to YouTube Live 24/7.

Works on **Render (Free)**, **Koyeb**, and **Railway** ☁️

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
[![Deploy to Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/inyogeshwar/24-7YouTubeMusicLiveBot)

## ✨ Features

- **24/7 Live**: Automatically loops your video and audio forever
- **Free to Run**: Optimized for Render Free Tier ($0/month)
- **Multi-Stream**: Run multiple streams using different Telegram Groups
- **Easy Uploads**: Send files directly to Telegram or use Google Drive links
- **No PC Needed**: Runs on the cloud, even if your phone/laptop is off
- **Auto-Restart**: Automatically restarts if the stream fails
- **High Quality**: Supports 1080p streaming with customizable bitrate
- **Multiple Formats**: Supports MP4, MKV, MP3, WAV, and more
- **🆕 Set Stream Key via Bot**: Configure YouTube stream key directly through Telegram
- **🆕 Live Video/Audio Switching**: Switch between files during live stream (StreamYard-like)
- **🆕 Per-Chat Stream Keys**: Each Telegram group can have its own stream key
- **🆕 Playlist Control**: Skip, previous, switch tracks during live stream

## 📋 Requirements

- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- YouTube Live Stream Key (from [YouTube Studio](https://studio.youtube.com))
- A free cloud platform account (Render, Koyeb, or Railway)

## 🚀 Quick Start

### Option 1: Deploy to Render (Recommended - Free Forever)

1. **Fork this repository** to your GitHub account

2. **Create a Render account** at [render.com](https://render.com)

3. **Create a new Web Service**:
   - Connect your GitHub repository
   - Select the forked repository
   - Use the following settings:
     - **Name**: `youtube-live-bot` (or any name)
     - **Region**: Choose closest to you
     - **Branch**: `main`
     - **Build Command**: `bash install.sh`
     - **Start Command**: `python bot.py`

4. **Add Environment Variables**:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   YOUTUBE_STREAM_KEY=your_stream_key_here
   YOUTUBE_RTMP_URL=rtmp://a.rtmp.youtube.com/live2/
   VIDEO_BITRATE=2500k
   AUDIO_BITRATE=128k
   VIDEO_RESOLUTION=1920x1080
   FPS=30
   STORAGE_PATH=/tmp/storage/
   ```

5. **Deploy** and wait for the service to start

### Option 2: Deploy to Railway

1. Click the "Deploy to Railway" button above
2. Fill in the required environment variables
3. Deploy!

### Option 3: Deploy to Koyeb

1. Create a Koyeb account at [koyeb.com](https://www.koyeb.com)
2. Create a new app from GitHub
3. Connect your forked repository
4. Add environment variables
5. Deploy!

### Option 4: Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/inyogeshwar/24-7YouTubeMusicLiveBot.git
   cd 24-7YouTubeMusicLiveBot
   ```

2. **Install FFmpeg**:
   - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your tokens.

5. **Run the bot**:
   ```bash
   python bot.py
   ```

## 🔧 Configuration

### Getting Your Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the token provided

### Getting Your YouTube Stream Key

1. Go to [YouTube Studio](https://studio.youtube.com)
2. Click on "Go Live" or "Create" → "Go Live"
3. Enable live streaming if not already enabled
4. Go to "Stream settings" → "Stream key"
5. Copy your stream key (keep it secret!)

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | - | ✅ Yes |
| `YOUTUBE_STREAM_KEY` | Your YouTube stream key (can also set via `/setkey`) | - | No* |
| `YOUTUBE_RTMP_URL` | YouTube RTMP URL | `rtmp://a.rtmp.youtube.com/live2/` | No |
| `VIDEO_BITRATE` | Video bitrate | `2500k` | No |
| `AUDIO_BITRATE` | Audio bitrate | `128k` | No |
| `VIDEO_RESOLUTION` | Video resolution | `1920x1080` | No |
| `FPS` | Frames per second | `30` | No |
| `ADMIN_USER_IDS` | Comma-separated admin IDs | - | No |
| `STORAGE_PATH` | File storage path | `./storage/` | No |

*Note: Stream key can be set via environment variable OR using the `/setkey` command in Telegram. The bot command takes precedence and allows per-chat configuration.

### Video Quality Settings

For different quality levels, use these settings:

**1080p (High Quality)**:
```
VIDEO_BITRATE=4500k
VIDEO_RESOLUTION=1920x1080
FPS=30
```

**720p (Medium Quality)**:
```
VIDEO_BITRATE=2500k
VIDEO_RESOLUTION=1280x720
FPS=30
```

**480p (Low Quality)**:
```
VIDEO_BITRATE=1000k
VIDEO_RESOLUTION=854x480
FPS=24
```

## 📱 Bot Commands

### Basic Commands

- `/start` - Show welcome message
- `/help` - Get detailed help
- `/upload` - Upload a video/audio file
- `/add_gdrive <link>` - Add a Google Drive file
- `/stream` - Start streaming to YouTube Live
- `/stop` - Stop the current stream
- `/status` - Check stream status
- `/list` - List all uploaded files

### Stream Key Commands (NEW!)

- `/setkey <key>` - Set YouTube stream key via Telegram
- `/setrtmp <url>` - Set custom RTMP URL (default: YouTube)
- `/showkey` - Show current stream key (masked for security)

### Live Control Commands (StreamYard-like features!)

- `/switch <number>` - Switch to a specific file during live stream
- `/next` - Skip to next file in playlist
- `/prev` - Go to previous file in playlist
- `/nowplaying` - Show currently playing file
- `/remove <number>` - Remove a file from playlist

### Usage Flow

1. **Start the bot**: Send `/start` to your bot
2. **Set stream key**: Use `/setkey <your_youtube_stream_key>`
3. **Upload files**: 
   - Send video/audio files directly
   - OR use `/add_gdrive <google_drive_link>`
4. **Start streaming**: Send `/stream`
5. **Control playback**: Use `/next`, `/prev`, or `/switch` to change content
6. **Check status**: Send `/status` or `/nowplaying` anytime
7. **Stop streaming**: Send `/stop` when done

## 🎯 Use Cases

### Music Radio Station
Upload your favorite music tracks and stream them 24/7 to create your own radio station.

### Podcast Channel
Upload podcast episodes and keep your channel live with continuous content.

### Video Loop
Upload a single video or multiple videos to loop them continuously.

### Study/Work Music
Stream lo-fi, jazz, or ambient music for your audience.

### Live DJ/VJ Sessions
Use the live switching feature to change tracks like a DJ during your stream!

## 🔐 Admin Access

By default, anyone can use your bot. To restrict access:

1. Get your Telegram User ID (send `/start` to [@userinfobot](https://t.me/userinfobot))
2. Add your ID to `ADMIN_USER_IDS` environment variable
3. Example: `ADMIN_USER_IDS=123456789,987654321`

## 🎨 Multi-Stream Setup

You can run multiple independent streams:

1. Create different Telegram groups
2. Add your bot to each group
3. Set a unique stream key for each group using `/setkey`
4. Each group maintains its own file library
5. Each group can stream independently to different YouTube channels

Example:
- **Group 1**: Music stream → YouTube Channel A (set with `/setkey key_a`)
- **Group 2**: Podcast stream → YouTube Channel B (set with `/setkey key_b`)
- **Group 3**: Video loop stream → YouTube Channel C (set with `/setkey key_c`)

## 🐛 Troubleshooting

### Bot Not Responding
- Check if the bot is running in your cloud platform dashboard
- Verify your `TELEGRAM_BOT_TOKEN` is correct
- Check logs for error messages

### Stream Not Starting
- Check stream key with `/showkey`
- Set stream key with `/setkey` if not configured
- Verify your `YOUTUBE_STREAM_KEY` is correct
- Make sure YouTube Live streaming is enabled on your channel
- Check if FFmpeg is installed (run `ffmpeg -version`)
- Ensure you have uploaded at least one file

### Poor Stream Quality
- Increase `VIDEO_BITRATE` for better quality
- Reduce bitrate if your connection is slow
- Try lowering resolution if needed

### Stream Keeps Stopping
- Check your cloud platform's resource limits
- Verify your internet connection is stable
- Monitor the logs for errors

### File Upload Failed
- Check file size (Telegram has 50MB limit for bots)
- For larger files, use Google Drive links
- Ensure supported format (MP4, MKV, MP3, WAV)

## 📊 Resource Usage

### Render Free Tier
- **750 hours/month** of runtime (enough for 24/7)
- Spins down after 15 minutes of inactivity
- Auto-wakes on Telegram message
- Free forever!

### Railway Free Tier
- **500 hours/month** of runtime
- $5 free credit monthly
- Always-on service

### Koyeb Free Tier
- **512MB RAM** free instance
- Limited to 1 service
- Automatic scaling

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## ⚠️ Disclaimer

This bot is for educational and personal use only. Make sure you have the rights to stream the content you upload. Respect YouTube's Terms of Service and copyright laws.

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [FFmpeg](https://ffmpeg.org/) - Video/audio processing
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloading utility

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/inyogeshwar/24-7YouTubeMusicLiveBot/issues) page
2. Open a new issue if your problem isn't listed
3. Provide detailed information about your setup and the error

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

Made with ❤️ for the streaming community