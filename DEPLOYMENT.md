# Deployment Guide

This guide provides detailed instructions for deploying the 24/7 YouTube Music Live Bot on different platforms.

## Table of Contents

- [24/7 Uptime Setup (Important!)](#247-uptime-setup-important)
- [Render Deployment](#render-deployment)
- [Railway Deployment](#railway-deployment)
- [Koyeb Deployment](#koyeb-deployment)
- [Docker Deployment](#docker-deployment)

## 24/7 Uptime Setup (Important!)

Free tier cloud platforms (Render, Koyeb, Railway) may put your service to sleep after a period of inactivity. This bot includes a built-in health check endpoint to keep it alive 24/7.

### How It Works

The bot runs a lightweight web server with health check endpoints:
- `/` - Root endpoint showing bot status
- `/health` - Health check endpoint (JSON response with uptime)
- `/ping` - Simple ping endpoint for keep-alive services

### Setting Up 24/7 Uptime

#### Option 1: Use UptimeRobot (Free - Recommended)

1. **Create an Account**
   - Visit https://uptimerobot.com
   - Sign up for a free account

2. **Add New Monitor**
   - Click "Add New Monitor"
   - Monitor Type: HTTP(s)
   - Friendly Name: `YouTube Live Bot`
   - URL: `https://your-app-name.onrender.com/health`
   - Monitoring Interval: 5 minutes
   - Click "Create Monitor"

3. **That's it!** UptimeRobot will ping your bot every 5 minutes, preventing it from sleeping.

#### Option 2: Use Freshping (Free)

1. Visit https://www.freshworks.com/website-monitoring/
2. Sign up for a free account
3. Add your health check URL: `https://your-app-name.onrender.com/health`
4. Set check interval to 1-5 minutes

#### Option 3: Use Cron-Job.org (Free)

1. Visit https://cron-job.org
2. Create a free account
3. Create a new cron job:
   - URL: `https://your-app-name.onrender.com/ping`
   - Schedule: Every 5 minutes
   - Request Method: GET

#### Option 4: Use Better Stack (Free Tier Available)

1. Visit https://betterstack.com/uptime
2. Create a free account
3. Add a new monitor with your health check URL

### Platform-Specific URLs

After deployment, your health check URL will be:

| Platform | Health Check URL |
|----------|-----------------|
| Render | `https://your-app-name.onrender.com/health` |
| Railway | `https://your-app-name.up.railway.app/health` |
| Koyeb | `https://your-app-name.koyeb.app/health` |

### Verify It's Working

1. Open your health check URL in a browser
2. You should see a JSON response like:
   ```json
   {
     "status": "healthy",
     "uptime": "2h 30m 15s",
     "message": "24/7 YouTube Music Live Bot is running!"
   }
   ```

## Render Deployment

### Prerequisites
- GitHub account
- Render account (free)
- Telegram Bot Token
- YouTube Stream Key

### Steps

1. **Fork the Repository**
   - Go to https://github.com/inyogeshwar/24-7YouTubeMusicLiveBot
   - Click "Fork" button
   - Fork to your GitHub account

2. **Sign Up for Render**
   - Visit https://render.com
   - Sign up using your GitHub account

3. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub account if not already connected
   - Select your forked repository
   - Click "Connect"

4. **Configure Service**
   - **Name**: `youtube-live-bot` (or your choice)
   - **Region**: Choose closest to you (e.g., Oregon, Frankfurt, Singapore)
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Runtime**: Python 3
   - **Build Command**: `bash install.sh`
   - **Start Command**: `python bot.py`
   - **Plan**: Free

5. **Add Environment Variables**
   
   Click "Advanced" → "Add Environment Variable" and add the following:
   
   ```
   TELEGRAM_BOT_TOKEN = your_bot_token_from_botfather
   YOUTUBE_STREAM_KEY = your_youtube_stream_key
   YOUTUBE_RTMP_URL = rtmp://a.rtmp.youtube.com/live2/
   VIDEO_BITRATE = 2500k
   AUDIO_BITRATE = 128k
   VIDEO_RESOLUTION = 1920x1080
   FPS = 30
   STORAGE_PATH = /tmp/storage/
   ADMIN_USER_IDS = your_telegram_user_id
   ```
   
   Note: Render automatically sets the PORT environment variable for web services.

6. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete (5-10 minutes)
   - Check logs for "Bot started successfully!" and "Web server started on port"

7. **Set Up Uptime Monitoring**
   - Copy your Render URL (e.g., `https://youtube-live-bot.onrender.com`)
   - Follow the [24/7 Uptime Setup](#247-uptime-setup-important) section above

8. **Test Your Bot**
   - Open Telegram
   - Search for your bot
   - Send `/start`
   - Upload a file or add a Google Drive link
   - Send `/stream` to start

### Render-Specific Tips

- **Health Check**: The built-in health check at `/health` keeps the service active
- **Uptime Monitoring**: Use UptimeRobot or similar to ping `/health` every 5 minutes
- **Free Hours**: 750 hours/month (enough for 24/7)
- **Logs**: View logs in Render dashboard → your service → Logs
- **Restart**: Manual restart available in dashboard

## Railway Deployment

### Prerequisites
- GitHub account
- Railway account
- Telegram Bot Token
- YouTube Stream Key

### Steps

1. **Sign Up for Railway**
   - Visit https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select your forked repository

3. **Add Environment Variables**
   
   Go to your service → Variables tab and add:
   
   ```
   TELEGRAM_BOT_TOKEN = your_bot_token
   YOUTUBE_STREAM_KEY = your_stream_key
   YOUTUBE_RTMP_URL = rtmp://a.rtmp.youtube.com/live2/
   VIDEO_BITRATE = 2500k
   AUDIO_BITRATE = 128k
   VIDEO_RESOLUTION = 1920x1080
   FPS = 30
   STORAGE_PATH = /tmp/storage/
   PORT = 8080
   ```

4. **Configure Build**
   - Railway auto-detects Python
   - Build command: `bash install.sh`
   - Start command: `python bot.py`

5. **Deploy**
   - Railway automatically deploys
   - Monitor logs for successful start

6. **Set Up Uptime Monitoring (Optional)**
   - Copy your Railway URL (e.g., `https://your-app.up.railway.app`)
   - Follow the [24/7 Uptime Setup](#247-uptime-setup-important) section

### Railway-Specific Tips

- **Health Check**: Access `/health` endpoint to verify bot status
- **Free Credit**: $5/month free credit
- **Resource Usage**: Monitor usage in dashboard
- **Always-On**: Railway keeps services running
- **Logs**: Real-time logs available

## Koyeb Deployment

### Prerequisites
- GitHub account
- Koyeb account
- Telegram Bot Token
- YouTube Stream Key

### Steps

1. **Sign Up for Koyeb**
   - Visit https://www.koyeb.com
   - Sign up with GitHub

2. **Create New App**
   - Click "Create App"
   - Select "GitHub" as source
   - Connect repository

3. **Configure App**
   - **Name**: `youtube-live-bot`
   - **Branch**: `main`
   - **Build command**: `bash install.sh`
   - **Run command**: `python bot.py`
   - **Instance type**: Nano (free)
   - **Port**: 8080

4. **Set Environment Variables**
   
   Add in the Environment Variables section:
   
   ```
   TELEGRAM_BOT_TOKEN = your_bot_token
   YOUTUBE_STREAM_KEY = your_stream_key
   YOUTUBE_RTMP_URL = rtmp://a.rtmp.youtube.com/live2/
   VIDEO_BITRATE = 2500k
   AUDIO_BITRATE = 128k
   VIDEO_RESOLUTION = 1920x1080
   FPS = 30
   STORAGE_PATH = /tmp/storage/
   PORT = 8080
   ```

5. **Configure Health Check**
   - Health Check Path: `/health`
   - This keeps your service alive and healthy

6. **Deploy**
   - Click "Deploy"
   - Wait for deployment

7. **Set Up Uptime Monitoring (Optional)**
   - Copy your Koyeb URL (e.g., `https://your-app.koyeb.app`)
   - Follow the [24/7 Uptime Setup](#247-uptime-setup-important) section

### Koyeb-Specific Tips

- **Health Check**: Built-in `/health` endpoint for monitoring
- **Free Tier**: 512MB RAM instance
- **Scaling**: Automatic scaling available
- **Uptime**: Use external monitoring for guaranteed 24/7 uptime

## Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose (optional)

### Using Docker

1. **Create Dockerfile** (already included in repo):
   ```dockerfile
   FROM python:3.11-slim
   
   # Install FFmpeg
   RUN apt-get update && \
       apt-get install -y ffmpeg && \
       apt-get clean && \
       rm -rf /var/lib/apt/lists/*
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   CMD ["python", "bot.py"]
   ```

2. **Build Image**:
   ```bash
   docker build -t youtube-live-bot .
   ```

3. **Run Container**:
   ```bash
   docker run -d \
     --name youtube-live-bot \
     -e TELEGRAM_BOT_TOKEN=your_token \
     -e YOUTUBE_STREAM_KEY=your_key \
     -e YOUTUBE_RTMP_URL=rtmp://a.rtmp.youtube.com/live2/ \
     -v $(pwd)/storage:/app/storage \
     youtube-live-bot
   ```

### Using Docker Compose

1. **Create docker-compose.yml** (already included):
   ```yaml
   version: '3.8'
   
   services:
     bot:
       build: .
       env_file:
         - .env
       volumes:
         - ./storage:/app/storage
       restart: unless-stopped
   ```

2. **Run**:
   ```bash
   docker-compose up -d
   ```

## Common Issues

### Issue: Bot not responding
**Solution**: 
- Check if service is running in dashboard
- Verify environment variables
- Check logs for errors

### Issue: Stream won't start
**Solution**:
- Verify YouTube stream key is correct
- Ensure FFmpeg is installed
- Check YouTube Live is enabled on your channel

### Issue: Service keeps restarting
**Solution**:
- Check logs for error messages
- Verify all dependencies are installed
- Ensure sufficient resources allocated

### Issue: Files not uploading
**Solution**:
- Check file size (Telegram limit: 50MB)
- Use Google Drive for larger files
- Verify storage path has write permissions

## Monitoring and Maintenance

### Logs
- **Render**: Dashboard → Service → Logs
- **Railway**: Dashboard → Service → Logs
- **Koyeb**: Dashboard → Service → Logs
- **Docker**: `docker logs youtube-live-bot`

### Restart Service
- **Render**: Dashboard → Manual Deploy → Deploy
- **Railway**: Dashboard → Service → Restart
- **Koyeb**: Dashboard → Service → Restart
- **Docker**: `docker restart youtube-live-bot`

### Update Code
1. Push changes to GitHub
2. Platform automatically redeploys
3. Or manually trigger deployment

## Performance Optimization

### For Free Tiers
- Use 720p instead of 1080p
- Lower bitrate to 1500k
- Reduce FPS to 24

### For Better Quality
- Upgrade to paid tier
- Use 1080p with 4500k bitrate
- Keep FPS at 30

## Security Best Practices

1. **Never commit `.env` file**
2. **Keep stream key secret**
3. **Use admin user IDs**
4. **Regularly rotate tokens**
5. **Monitor usage logs**

## Support

For deployment issues:
1. Check platform-specific documentation
2. Review error logs
3. Open an issue on GitHub
4. Join our community discussions

---

Need help? Open an issue: https://github.com/inyogeshwar/24-7YouTubeMusicLiveBot/issues
