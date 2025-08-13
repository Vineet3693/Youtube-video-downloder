
import re
from urllib.parse import urlparse, parse_qs
from typing import Optional

class URLValidator:
    
    YOUTUBE_VIDEO_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:m\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})'
    ]
    
    YOUTUBE_PLAYLIST_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?.*list=([a-zA-Z0-9_-]+)'
    ]
    
    @classmethod
    def is_valid_youtube_url(cls, url: str) -> bool:
        """Check if URL is a valid YouTube video URL."""
        if not url:
            return False
        
        for pattern in cls.YOUTUBE_VIDEO_PATTERNS:
            if re.match(pattern, url):
                return True
        return False
    
    @classmethod
    def is_valid_youtube_playlist_url(cls, url: str) -> bool:
        """Check if URL is a valid YouTube playlist URL."""
        if not url:
            return False
        
        for pattern in cls.YOUTUBE_PLAYLIST_PATTERNS:
            if re.match(pattern, url):
                return True
        return False
    
    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        for pattern in cls.YOUTUBE_VIDEO_PATTERNS:
            match = re.match(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @classmethod
    def extract_playlist_id(cls, url: str) -> Optional[str]:
        """Extract playlist ID from YouTube URL."""
        for pattern in cls.YOUTUBE_PLAYLIST_PATTERNS:
            match = re.match(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @classmethod
    def normalize_url(cls, url: str) -> str:
        """Normalize YouTube URL to standard format."""
        if cls.is_valid_youtube_url(url):
            video_id = cls.extract_video_id(url)
            if video_id:
                return f"https://www.youtube.com/watch?v={video_id}"
        
        if cls.is_valid_youtube_playlist_url(url):
            playlist_id = cls.extract_playlist_id(url)
            if playlist_id:
                return f"https://www.youtube.com/playlist?list={playlist_id}"
        
        return url
