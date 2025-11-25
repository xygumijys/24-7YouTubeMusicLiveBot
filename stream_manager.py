"""
Stream Manager Module
Handles YouTube Live streaming with FFmpeg
"""

import os
import asyncio
import logging
import tempfile
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
        self.stream_keys: Dict[int, str] = {}  # chat_id -> YouTube stream key
        self.rtmp_urls: Dict[int, str] = {}  # chat_id -> RTMP URL
        self._restart_requested: Dict[int, bool] = {}  # chat_id -> restart flag for live switching
        
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
    
    def set_stream_key(self, chat_id: int, stream_key: str) -> None:
        """Set YouTube stream key for a chat"""
        self.stream_keys[chat_id] = stream_key
        logger.info(f"Stream key set for chat {chat_id}")
    
    def get_stream_key(self, chat_id: int) -> Optional[str]:
        """Get YouTube stream key for a chat"""
        # First check per-chat key, then fall back to environment variable
        return self.stream_keys.get(chat_id) or os.getenv('YOUTUBE_STREAM_KEY')
    
    def set_rtmp_url(self, chat_id: int, rtmp_url: str) -> None:
        """Set custom RTMP URL for a chat"""
        self.rtmp_urls[chat_id] = rtmp_url
        logger.info(f"RTMP URL set for chat {chat_id}")
    
    def get_rtmp_url(self, chat_id: int) -> str:
        """Get RTMP URL for a chat"""
        return self.rtmp_urls.get(chat_id) or os.getenv('YOUTUBE_RTMP_URL', 'rtmp://a.rtmp.youtube.com/live2/')
    
    def reset_rtmp_url(self, chat_id: int) -> None:
        """Reset RTMP URL to default for a chat"""
        self.rtmp_urls.pop(chat_id, None)
        logger.info(f"RTMP URL reset to default for chat {chat_id}")
    
    def remove_file(self, chat_id: int, file_index: int) -> Optional[str]:
        """Remove a file from the chat's library by index"""
        files = self.files.get(chat_id, [])
        if 0 <= file_index < len(files):
            removed = files.pop(file_index)
            logger.info(f"Removed file {removed} from chat {chat_id}")
            return removed
        return None
    
    def get_current_file_index(self, chat_id: int) -> int:
        """Get current playing file index"""
        if chat_id in self.streams:
            return self.streams[chat_id].get('current_file_index', 0)
        return 0
    
    def set_current_file_index(self, chat_id: int, index: int) -> bool:
        """Set current file index for switching"""
        files = self.get_files(chat_id)
        if 0 <= index < len(files):
            if chat_id in self.streams:
                self.streams[chat_id]['current_file_index'] = index
            return True
        return False
    
    async def switch_to_file(self, chat_id: int, file_index: int) -> bool:
        """Switch to a specific file during live stream"""
        files = self.get_files(chat_id)
        if not (0 <= file_index < len(files)):
            logger.error(f"Invalid file index {file_index} for chat {chat_id}")
            return False
        
        if not self.is_streaming(chat_id):
            # Just update the index if not streaming
            return self.set_current_file_index(chat_id, file_index)
        
        # Mark restart requested and stop current stream
        self._restart_requested[chat_id] = True
        self.set_current_file_index(chat_id, file_index)
        
        # Stop current stream
        await self.stop_stream(chat_id)
        
        # Restart with new file order
        success = await self.start_stream(chat_id, start_index=file_index)
        self._restart_requested.pop(chat_id, None)
        
        return success
    
    async def next_file(self, chat_id: int) -> bool:
        """Skip to next file in playlist"""
        files = self.get_files(chat_id)
        if not files:
            return False
        
        current_index = self.get_current_file_index(chat_id)
        next_index = (current_index + 1) % len(files)
        return await self.switch_to_file(chat_id, next_index)
    
    async def prev_file(self, chat_id: int) -> bool:
        """Go to previous file in playlist"""
        files = self.get_files(chat_id)
        if not files:
            return False
        
        current_index = self.get_current_file_index(chat_id)
        prev_index = (current_index - 1) % len(files)
        return await self.switch_to_file(chat_id, prev_index)
    
    async def start_stream(self, chat_id: int, start_index: int = 0) -> bool:
        """Start streaming for a chat"""
        if self.is_streaming(chat_id):
            logger.warning(f"Stream already active for chat {chat_id}")
            return False
        
        files = self.get_files(chat_id)
        if not files:
            logger.error(f"No files available for chat {chat_id}")
            return False
        
        # Get YouTube streaming configuration (per-chat or from env)
        stream_key = self.get_stream_key(chat_id)
        rtmp_url = self.get_rtmp_url(chat_id)
        
        if not stream_key:
            logger.error("No stream key configured for this chat")
            return False
        
        full_rtmp_url = f"{rtmp_url}{stream_key}"
        
        # Get stream settings
        video_bitrate = os.getenv('VIDEO_BITRATE', '2500k')
        audio_bitrate = os.getenv('AUDIO_BITRATE', '128k')
        resolution = os.getenv('VIDEO_RESOLUTION', '1920x1080')
        fps = os.getenv('FPS', '30')
        
        # Parse video bitrate (handle formats like "2500k" or "2500")
        try:
            bitrate_value = int(video_bitrate.rstrip('kK'))
            bufsize = f"{bitrate_value * 2}k"
        except (ValueError, AttributeError):
            logger.warning(f"Invalid VIDEO_BITRATE format: {video_bitrate}, using default bufsize")
            bufsize = "5000k"
        
        try:
            # Create FFmpeg command for looping and streaming
            # Use concat demuxer for smooth looping
            # Reorder files to start from the specified index
            ordered_files = files[start_index:] + files[:start_index]
            concat_file = self._create_concat_file(chat_id, ordered_files)
            
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
                '-bufsize', bufsize,
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
                'current_file_index': start_index
            }
            self.processes[chat_id] = process
            
            logger.info(f"Started stream for chat {chat_id} with {len(files)} file(s) starting at index {start_index}")
            
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
                
                # Clean up concat file (cross-platform)
                concat_file = os.path.join(tempfile.gettempdir(), f"concat_{chat_id}.txt")
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
        concat_file = os.path.join(tempfile.gettempdir(), f"concat_{chat_id}.txt")
        
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
                # Check if this was a requested restart (e.g., for file switching)
                if self._restart_requested.get(chat_id):
                    logger.info(f"Stream stopped for chat {chat_id} due to requested switch")
                    break
                
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
