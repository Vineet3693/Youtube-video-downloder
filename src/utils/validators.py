
import re

class URLValidator:
    @staticmethod
    def is_valid_youtube_url(url: str) -> bool:
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
        ]
        return any(re.search(pattern, url) for pattern in patterns)
    
    @staticmethod
    def is_valid_youtube_playlist_url(url: str) -> bool:
        return 'youtube.com/playlist' in url or 'list=' in url
    
    @staticmethod
    def normalize_url(url: str) -> str:
        return url.strip()
