"""
Stream Manager Module
Handles YouTube Live streaming with FFmpeg
"""

import os
import asyncio
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime
import subprocess

logger = logging.getLogger(__name__)


class StreamManager:
    """Manages YouTube Live streams for multiple chats"""
    
    def __init__(self):
        self.streams: Dict[int, Dict] = {}  # chat_id -> stream info
        self.files: Dict[int, List[str]] = {}  # chat_id -> list of file paths
        self.processes: Dict[int, subprocess.Popen] = {}  # chat_id -> FFmpeg process
        
    def add_file(self, chat_id: int, file_path: str) -> None:
        """Add a file to the chat's library"""
        if chat_id not in self.files:
            self.files[chat_id] = []
        
        if file_path not in self.files[chat_id]:
            self.files[chat_id].append(file_path)
            logger.info(f"Added file {file_path} to chat {chat_id}")
    
    def get_files(self, chat_id: int) -> List[str]:
        """Get all files for a chat"""
        return self.files.get(chat_id, [])
    
    def is_streaming(self, chat_id: int) -> bool:
        """Check if a stream is active for a chat"""
        if chat_id not in self.streams:
            return False
        
        # Check if process is still running
        if chat_id in self.processes:
            process = self.processes[chat_id]
            if process.poll() is None:
                return True
            else:
                # Process died, clean up
                self.streams.pop(chat_id, None)
                self.processes.pop(chat_id, None)
                return False
        
        return False
    
    async def start_stream(self, chat_id: int) -> bool:
        """Start streaming for a chat"""
        if self.is_streaming(chat_id):
            logger.warning(f"Stream already active for chat {chat_id}")
            return False
        
        files = self.get_files(chat_id)
        if not files:
            logger.error(f"No files available for chat {chat_id}")
            return False
        
        # Get YouTube streaming configuration
        stream_key = os.getenv('YOUTUBE_STREAM_KEY')
        rtmp_url = os.getenv('YOUTUBE_RTMP_URL', 'rtmp://a.rtmp.youtube.com/live2/')
        
        if not stream_key:
            logger.error("YOUTUBE_STREAM_KEY not configured")
            return False
        
        full_rtmp_url = f"{rtmp_url}{stream_key}"
        
        # Get stream settings
        video_bitrate = os.getenv('VIDEO_BITRATE', '2500k')
        audio_bitrate = os.getenv('AUDIO_BITRATE', '128k')
        resolution = os.getenv('VIDEO_RESOLUTION', '1920x1080')
        fps = os.getenv('FPS', '30')
        
        try:
            # Create FFmpeg command for looping and streaming
            # Use concat demuxer for smooth looping
            concat_file = self._create_concat_file(chat_id, files)
            
            ffmpeg_cmd = [
                'ffmpeg',
                '-re',  # Read input at native frame rate
                '-stream_loop', '-1',  # Loop indefinitely
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c:v', 'libx264',  # Video codec
                '-preset', 'veryfast',  # Encoding preset
                '-b:v', video_bitrate,  # Video bitrate
                '-maxrate', video_bitrate,
                '-bufsize', str(int(video_bitrate.replace('k', '')) * 2) + 'k',
                '-s', resolution,  # Resolution
                '-r', fps,  # Frame rate
                '-g', str(int(fps) * 2),  # GOP size
                '-c:a', 'aac',  # Audio codec
                '-b:a', audio_bitrate,  # Audio bitrate
                '-ar', '44100',  # Audio sample rate
                '-f', 'flv',  # Output format
                full_rtmp_url
            ]
            
            # Start FFmpeg process
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL
            )
            
            # Store stream info
            self.streams[chat_id] = {
                'started_at': datetime.now(),
                'files': files.copy(),
                'current_file_index': 0
            }
            self.processes[chat_id] = process
            
            logger.info(f"Started stream for chat {chat_id} with {len(files)} file(s)")
            
            # Start monitoring task
            asyncio.create_task(self._monitor_stream(chat_id))
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting stream for chat {chat_id}: {e}")
            return False
    
    async def stop_stream(self, chat_id: int) -> None:
        """Stop streaming for a chat"""
        if chat_id in self.processes:
            process = self.processes[chat_id]
            try:
                process.terminate()
                await asyncio.sleep(2)
                if process.poll() is None:
                    process.kill()
                logger.info(f"Stopped stream for chat {chat_id}")
            except Exception as e:
                logger.error(f"Error stopping stream for chat {chat_id}: {e}")
            finally:
                self.processes.pop(chat_id, None)
                self.streams.pop(chat_id, None)
                
                # Clean up concat file
                concat_file = f"/tmp/concat_{chat_id}.txt"
                if os.path.exists(concat_file):
                    os.remove(concat_file)
    
    def get_status(self, chat_id: int) -> Dict:
        """Get stream status for a chat"""
        if not self.is_streaming(chat_id):
            return {
                'is_streaming': False,
                'total_files': len(self.get_files(chat_id))
            }
        
        stream_info = self.streams[chat_id]
        started_at = stream_info['started_at']
        uptime = datetime.now() - started_at
        
        # Format uptime
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours}h {minutes}m {seconds}s"
        
        files = stream_info['files']
        current_index = stream_info['current_file_index']
        current_file = os.path.basename(files[current_index]) if files else "Unknown"
        
        return {
            'is_streaming': True,
            'uptime': uptime_str,
            'current_file': current_file,
            'total_files': len(files)
        }
    
    def _create_concat_file(self, chat_id: int, files: List[str]) -> str:
        """Create a concat file for FFmpeg"""
        concat_file = f"/tmp/concat_{chat_id}.txt"
        
        with open(concat_file, 'w') as f:
            for file_path in files:
                # Escape single quotes in file path
                escaped_path = file_path.replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")
        
        return concat_file
    
    async def _monitor_stream(self, chat_id: int) -> None:
        """Monitor stream health and restart if needed"""
        while chat_id in self.processes:
            process = self.processes[chat_id]
            
            # Check if process is still running
            if process.poll() is not None:
                logger.warning(f"Stream process died for chat {chat_id}, attempting restart...")
                
                # Clean up
                self.processes.pop(chat_id, None)
                self.streams.pop(chat_id, None)
                
                # Wait a bit before restarting
                await asyncio.sleep(5)
                
                # Attempt restart
                if self.get_files(chat_id):
                    logger.info(f"Restarting stream for chat {chat_id}")
                    await self.start_stream(chat_id)
                    break
                else:
                    logger.error(f"Cannot restart stream for chat {chat_id}: no files")
                    break
            
            # Wait before next check
            await asyncio.sleep(30)
