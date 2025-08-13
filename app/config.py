
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    # App Settings
    APP_NAME = "YouTube Downloader"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Download Settings
    DEFAULT_QUALITY = "720p"
    DEFAULT_FORMAT = "mp4"
    MAX_CONCURRENT_DOWNLOADS = 3
    DOWNLOAD_TIMEOUT = 300  # seconds
    
    # File Settings
    MAX_FILE_SIZE_MB = 500
    ALLOWED_FORMATS = ["mp4", "webm", "mp3"]
    TEMP_DIR = Path(os.getenv("TEMP_DIR", "/tmp/youtube_downloads"))
    
    # UI Settings
    THEME = "light"
    MAX_PLAYLIST_SIZE = 100
    
    # API Settings
    RATE_LIMIT_PER_MINUTE = 30
    
    @classmethod
    def get_download_config(cls) -> Dict[str, Any]:
        return {
            "quality": cls.DEFAULT_QUALITY,
            "format": cls.DEFAULT_FORMAT,
            "max_concurrent": cls.MAX_CONCURRENT_DOWNLOADS,
            "timeout": cls.DOWNLOAD_TIMEOUT,
            "max_file_size": cls.MAX_FILE_SIZE_MB
        }
    
    @classmethod
    def create_temp_dir(cls) -> Path:
        cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        return cls.TEMP_DIR
