"""
File Handler Module
Handles file downloads from Telegram and Google Drive
"""

import os
import logging
import re
from typing import Optional
import aiohttp

logger = logging.getLogger(__name__)


class FileHandler:
    """Handles file downloads and management"""
    
    def __init__(self):
        self.storage_path = os.getenv('STORAGE_PATH', './storage/')
        os.makedirs(self.storage_path, exist_ok=True)
    
    async def download_telegram_file(self, file, file_name: str, bot) -> str:
        """Download a file from Telegram"""
        try:
            # Get file from Telegram
            telegram_file = await bot.get_file(file.file_id)
            
            # Create safe filename
            safe_name = self._sanitize_filename(file_name)
            file_path = os.path.join(self.storage_path, safe_name)
            
            # Download file
            await telegram_file.download_to_drive(file_path)
            
            logger.info(f"Downloaded Telegram file: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error downloading Telegram file: {e}")
            raise
    
    async def download_from_gdrive(self, gdrive_link: str) -> str:
        """Download a file from Google Drive"""
        try:
            # Extract file ID from Google Drive link
            file_id = self._extract_gdrive_id(gdrive_link)
            if not file_id:
                raise ValueError("Invalid Google Drive link")
            
            # Use direct download link
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            # Create filename
            file_name = f"gdrive_{file_id}"
            file_path = os.path.join(self.storage_path, file_name)
            
            # Download file
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as response:
                    if response.status == 200:
                        with open(file_path, 'wb') as f:
                            while True:
                                chunk = await response.content.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                    else:
                        raise Exception(f"Failed to download: HTTP {response.status}")
            
            # Try to detect file extension
            file_path = await self._detect_and_rename_file(file_path)
            
            logger.info(f"Downloaded Google Drive file: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error downloading from Google Drive: {e}")
            raise
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to remove invalid characters"""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        name, ext = os.path.splitext(filename)
        if len(name) > 200:
            name = name[:200]
        return name + ext
    
    def _extract_gdrive_id(self, link: str) -> Optional[str]:
        """Extract file ID from Google Drive link"""
        patterns = [
            r'/file/d/([a-zA-Z0-9_-]+)',
            r'id=([a-zA-Z0-9_-]+)',
            r'/open\?id=([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, link)
            if match:
                return match.group(1)
        
        return None
    
    async def _detect_and_rename_file(self, file_path: str) -> str:
        """Detect file type and rename with proper extension"""
        try:
            # Try to detect file type using file command (if available)
            import subprocess
            result = subprocess.run(
                ['file', '--mime-type', '-b', file_path],
                capture_output=True,
                text=True
            )
            
            mime_type = result.stdout.strip()
            
            # Map mime types to extensions
            mime_to_ext = {
                'video/mp4': '.mp4',
                'video/x-matroska': '.mkv',
                'video/x-msvideo': '.avi',
                'audio/mpeg': '.mp3',
                'audio/wav': '.wav',
                'audio/x-wav': '.wav',
            }
            
            if mime_type in mime_to_ext:
                new_path = file_path + mime_to_ext[mime_type]
                os.rename(file_path, new_path)
                return new_path
            
        except Exception as e:
            logger.warning(f"Could not detect file type: {e}")
        
        return file_path
