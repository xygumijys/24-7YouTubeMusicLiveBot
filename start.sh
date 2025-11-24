#!/bin/bash

# Quick Start Script for 24/7 YouTube Music Live Bot
# This script helps you set up and run the bot locally

set -e

echo "🎵 24/7 YouTube Music Live Bot - Quick Start"
echo "============================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Check FFmpeg
echo "📋 Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed."
    echo "   Please install FFmpeg:"
    echo "   - Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "   - macOS: brew install ffmpeg"
    echo "   - Windows: Download from https://ffmpeg.org/download.html"
    exit 1
fi

FFMPEG_VERSION=$(ffmpeg -version | head -n 1)
echo "✅ $FFMPEG_VERSION"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Setup environment variables
if [ ! -f ".env" ]; then
    echo "⚙️  Setting up environment variables..."
    cp .env.example .env
    echo "✅ .env file created from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your tokens:"
    echo "   1. TELEGRAM_BOT_TOKEN - Get from @BotFather"
    echo "   2. YOUTUBE_STREAM_KEY - Get from YouTube Studio"
    echo ""
    echo "   nano .env  # or use your preferred editor"
    echo ""
    read -p "Press Enter after editing .env file..."
else
    echo "✅ .env file already exists"
fi
echo ""

# Create storage directory
mkdir -p storage
echo "✅ Storage directory created"
echo ""

# Check if tokens are configured
echo "🔍 Checking configuration..."
source .env

if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "your_telegram_bot_token_here" ]; then
    echo "⚠️  TELEGRAM_BOT_TOKEN is not configured in .env"
    exit 1
fi

if [ -z "$YOUTUBE_STREAM_KEY" ] || [ "$YOUTUBE_STREAM_KEY" = "your_youtube_stream_key_here" ]; then
    echo "⚠️  YOUTUBE_STREAM_KEY is not configured in .env"
    exit 1
fi

echo "✅ Configuration looks good"
echo ""

# Start the bot
echo "🚀 Starting the bot..."
echo "   Press Ctrl+C to stop"
echo ""
python bot.py
