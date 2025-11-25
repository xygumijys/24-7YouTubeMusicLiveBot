# Deployment Guide

This guide provides detailed instructions for deploying the 24/7 YouTube Music Live Bot on different platforms.

## Table of Contents

- [Render Deployment](#render-deployment)
- [Railway Deployment](#railway-deployment)
- [Koyeb Deployment](#koyeb-deployment)
- [Docker Deployment](#docker-deployment)

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

6. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete (5-10 minutes)
   - Check logs for "Bot started successfully!"

7. **Test Your Bot**
   - Open Telegram
   - Search for your bot
   - Send `/start`
   - Upload a file or add a Google Drive link
   - Send `/stream` to start

### Render-Specific Tips

- **Auto-Sleep**: Free tier sleeps after 15 minutes of inactivity
- **Wake-Up**: Bot automatically wakes when you send a message
- **Logs**: View logs in Render dashboard → your service → Logs
- **Restart**: Manual restart available in dashboard
- **Free Hours**: 750 hours/month (enough for 24/7 with sleep)

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
   ```

4. **Configure Build**
   - Railway auto-detects Python
   - Build command: `bash install.sh`
   - Start command: `python bot.py`

5. **Deploy**
   - Railway automatically deploys
   - Monitor logs for successful start

### Railway-Specific Tips

- **Free Credit**: $5/month free credit
- **Resource Usage**: Monitor usage in dashboard
- **Always-On**: No sleep on free tier
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

4. **Set Environment Variables**
   
   Add in the Environment Variables section:
   
   ```
   TELEGRAM_BOT_TOKEN
   YOUTUBE_STREAM_KEY
   YOUTUBE_RTMP_URL
   VIDEO_BITRATE
   AUDIO_BITRATE
   VIDEO_RESOLUTION
   FPS
   STORAGE_PATH
   ```

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment

### Koyeb-Specific Tips

- **Free Tier**: 512MB RAM instance
- **Scaling**: Automatic scaling available
- **Health Checks**: Configure in settings

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
