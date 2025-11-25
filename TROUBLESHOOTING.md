# Troubleshooting Guide

This guide helps you resolve common issues with the 24/7 YouTube Music Live Bot.

## Table of Contents

- [Bot Issues](#bot-issues)
- [Streaming Issues](#streaming-issues)
- [File Upload Issues](#file-upload-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [Performance Issues](#performance-issues)

## Bot Issues

### Bot Not Responding

**Symptoms**: Bot doesn't reply to messages

**Possible Causes & Solutions**:

1. **Bot Token Invalid**
   - Check `TELEGRAM_BOT_TOKEN` in environment variables
   - Get new token from @BotFather if needed
   - Ensure no extra spaces in token

2. **Bot Not Running**
   - Check platform dashboard (Render/Railway/Koyeb)
   - View logs for errors
   - Manually restart the service

3. **Network Issues**
   - Check if Telegram is accessible
   - Verify platform has internet access
   - Check firewall settings

**Debug Steps**:
```bash
# Check if bot process is running
ps aux | grep bot.py

# Check logs
tail -f /var/log/bot.log  # or platform-specific log location

# Test bot token
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

### Bot Crashes on Start

**Symptoms**: Bot starts then immediately crashes

**Possible Causes & Solutions**:

1. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **FFmpeg Not Installed**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # macOS
   brew install ffmpeg
   ```

3. **Permission Issues**
   ```bash
   # Ensure storage directory is writable
   chmod 755 storage/
   ```

4. **Environment Variables Missing**
   - Check all required variables are set
   - Verify `.env` file is loaded

**Debug Steps**:
```bash
# Run with verbose logging
python bot.py --verbose

# Check Python version
python --version  # Should be 3.9+

# Test imports
python -c "import telegram; print('OK')"
```

### Command Not Working

**Symptoms**: Specific command doesn't respond

**Solutions**:

1. **Check Command Syntax**
   - Commands are case-sensitive
   - Use `/start` not `start`
   - Check `/help` for correct usage

2. **Admin Restrictions**
   - Some commands require admin access
   - Check `ADMIN_USER_IDS` configuration
   - Get your user ID from @userinfobot

3. **Bot Updates**
   - Restart bot after code changes
   - Clear Telegram cache
   - Try in a new chat

## Streaming Issues

### Stream Won't Start

**Symptoms**: `/stream` command fails

**Possible Causes & Solutions**:

1. **No Files Uploaded**
   ```
   Use /list to check files
   Upload at least one file before streaming
   ```

2. **Invalid Stream Key**
   - Verify `YOUTUBE_STREAM_KEY` is correct
   - Get fresh key from YouTube Studio
   - Check for extra spaces or characters

3. **YouTube Live Not Enabled**
   - Enable live streaming in YouTube Studio
   - Verify account is verified
   - Wait 24 hours after first enabling

4. **FFmpeg Issues**
   ```bash
   # Test FFmpeg
   ffmpeg -version
   
   # Test streaming capability
   ffmpeg -re -i test.mp4 -c copy -f flv rtmp://test
   ```

**Debug Steps**:
```bash
# Check stream process
ps aux | grep ffmpeg

# View FFmpeg output
# (Add logging to stream_manager.py if needed)

# Test RTMP connection
telnet a.rtmp.youtube.com 1935
```

### Stream Keeps Stopping

**Symptoms**: Stream starts but stops frequently

**Possible Causes & Solutions**:

1. **Network Issues**
   - Check internet stability
   - Use lower bitrate settings
   - Try different RTMP server

2. **Resource Limitations**
   - Upgrade from free tier
   - Reduce video quality
   - Lower resolution/bitrate

3. **File Issues**
   - Corrupt video files
   - Unsupported codecs
   - Re-encode problematic files

4. **YouTube Issues**
   - Check YouTube Live status
   - Verify stream key hasn't changed
   - Check YouTube Live dashboard for errors

**Solutions**:
```env
# Try lower quality settings
VIDEO_BITRATE=1500k
VIDEO_RESOLUTION=1280x720
FPS=24
```

### Poor Stream Quality

**Symptoms**: Blurry or pixelated stream

**Solutions**:

1. **Increase Bitrate**
   ```env
   VIDEO_BITRATE=4500k  # for 1080p
   AUDIO_BITRATE=192k
   ```

2. **Check Source Quality**
   - Use high-quality source files
   - Avoid re-encoding multiple times
   - Use proper video codecs

3. **Network Bandwidth**
   - Ensure sufficient upload speed
   - Test with speedtest
   - Use stable connection

### Stream Delay/Lag

**Symptoms**: Stream has significant delay

**Solutions**:

1. **YouTube Latency Settings**
   - Go to YouTube Studio
   - Stream Settings → Latency
   - Choose "Low latency"

2. **Reduce Buffer**
   ```env
   # Adjust in stream_manager.py
   bufsize = VIDEO_BITRATE
   ```

3. **Network Optimization**
   - Use wired connection if possible
   - Close other bandwidth-heavy applications
   - Choose closer RTMP server

## File Upload Issues

### Telegram Upload Fails

**Symptoms**: Cannot upload files to bot

**Solutions**:

1. **File Size Limit**
   - Telegram bots: 50MB limit
   - Use Google Drive for larger files
   - Compress files if possible

2. **File Format**
   - Supported: MP4, MKV, MP3, WAV
   - Convert unsupported formats
   ```bash
   ffmpeg -i input.avi -c:v libx264 output.mp4
   ```

3. **Permissions**
   - Check storage directory exists
   - Verify write permissions
   ```bash
   mkdir -p storage
   chmod 755 storage
   ```

### Google Drive Download Fails

**Symptoms**: `/add_gdrive` command fails

**Solutions**:

1. **File Not Public**
   - Share file publicly or with service account
   - Anyone with link can view
   - Check sharing settings

2. **Invalid Link**
   - Use full Google Drive link
   - Format: `https://drive.google.com/file/d/FILE_ID/view`
   - Try different link format

3. **File Too Large**
   - Google Drive has download limits
   - Try smaller files
   - Use direct download if possible

4. **Quota Exceeded**
   - Google Drive daily quota
   - Wait 24 hours
   - Use different files

## Platform-Specific Issues

### Render Issues

**Problem**: Service sleeps after 15 minutes

**Solution**: 
- Expected behavior on free tier
- Bot wakes on new message
- Upgrade to paid tier for always-on

**Problem**: Deployment fails

**Solutions**:
```bash
# Check build command
bash install.sh

# Verify start command
python bot.py

# Check logs for specific error
```

### Railway Issues

**Problem**: Out of credits

**Solution**:
- Monitor usage in dashboard
- $5 free credit per month
- Optimize resource usage
- Upgrade plan

**Problem**: Build fails

**Solutions**:
```bash
# Verify railway.json
# Check buildCommand
# Review deployment logs
```

### Koyeb Issues

**Problem**: Instance keeps restarting

**Solutions**:
- Check memory usage (512MB limit)
- Reduce video quality settings
- Monitor application logs

**Problem**: Health check fails

**Solutions**:
- Verify bot starts successfully
- Check if port binding is needed
- Review health check settings

### Docker Issues

**Problem**: Container won't start

**Solutions**:
```bash
# Check container logs
docker logs youtube-live-bot

# Verify environment variables
docker inspect youtube-live-bot

# Rebuild image
docker-compose build --no-cache
docker-compose up -d
```

**Problem**: Permission denied

**Solutions**:
```bash
# Fix volume permissions
sudo chown -R 1000:1000 storage/

# Or run with user
docker run --user $(id -u):$(id -g) ...
```

## Performance Issues

### High CPU Usage

**Causes & Solutions**:

1. **Multiple Streams**
   - Limit concurrent streams
   - Increase resources
   - Use lower encoding settings

2. **FFmpeg Encoding**
   ```env
   # Use faster preset
   # Modify stream_manager.py
   -preset veryfast  # or ultrafast
   ```

### High Memory Usage

**Solutions**:

1. **Clear Old Files**
   ```bash
   # Remove unused files from storage
   rm storage/old_file.mp4
   ```

2. **Limit File Cache**
   - Delete files after streaming
   - Use streaming from URL
   - Implement file rotation

### Slow File Downloads

**Solutions**:

1. **Network Speed**
   - Check internet connection
   - Use faster hosting
   - Optimize download code

2. **File Size**
   - Use compressed files
   - Lower quality sources
   - Implement chunked downloads

## Getting More Help

### Logs and Debugging

**View Logs**:
```bash
# Local
python bot.py > bot.log 2>&1

# Render
Dashboard → Service → Logs

# Railway  
Dashboard → Service → Deployments → View Logs

# Docker
docker logs youtube-live-bot -f
```

**Enable Debug Mode**:
```python
# In bot.py
logging.basicConfig(
    level=logging.DEBUG  # Change from INFO
)
```

### Reporting Issues

When reporting issues, include:

1. **Environment**:
   - Platform (Render/Railway/Koyeb/Docker)
   - Python version
   - FFmpeg version

2. **Error Details**:
   - Full error message
   - Relevant logs
   - Steps to reproduce

3. **Configuration** (without secrets):
   - Video settings
   - Bot commands used
   - File types uploaded

### Community Support

- **GitHub Issues**: https://github.com/inyogeshwar/24-7YouTubeMusicLiveBot/issues
- **Discussions**: https://github.com/inyogeshwar/24-7YouTubeMusicLiveBot/discussions
- **Documentation**: Check README.md and DEPLOYMENT.md

### Quick Fixes

**Reset Everything**:
```bash
# Stop service
# Clear storage
rm -rf storage/*

# Reset environment
cp .env.example .env
# Re-configure .env

# Restart bot
python bot.py
```

**Fresh Deployment**:
1. Delete existing deployment
2. Fork repository again
3. Create new deployment
4. Configure environment variables
5. Deploy

---

Still having issues? Open an issue with detailed information!
