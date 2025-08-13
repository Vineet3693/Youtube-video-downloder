
from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime

@dataclass
class VideoInfo:
    """Data model for video information."""
    
    id: str
    title: str
    url: str
    duration: Optional[int] = None  # in seconds
    view_count: Optional[int] = None
    upload_date: Optional[str] = None
    uploader: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    format_info: Optional[Dict] = None
    
    def __post_init__(self):
        # Sanitize title
        if self.title:
            self.title = self._sanitize_title(self.title)
    
    def _sanitize_title(self, title: str) -> str:
        """Sanitize video title."""
        # Remove/replace problematic characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '_')
        return title.strip()
    
    def get_duration_formatted(self) -> str:
        """Get formatted duration string."""
        if not self.duration:
            return "Unknown"
        
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def get_view_count_formatted(self) -> str:
        """Get formatted view count."""
        if not self.view_count:
            return "Unknown"
        
        if self.view_count >= 1_000_000:
            return f"{self.view_count / 1_000_000:.1f}M"
        elif self.view_count >= 1_000:
            return f"{self.view_count / 1_000:.1f}K"
        else:
            return str(self.view_count)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'duration': self.duration,
            'view_count': self.view_count,
            'upload_date': self.upload_date,
            'uploader': self.uploader,
            'description': self.description,
            'thumbnail_url': self.thumbnail_url,
            'format_info': self.format_info
        }

@dataclass
class DownloadResult:
    """Data model for download results."""
    
    video_info: VideoInfo
    success: bool
    file_path: Optional[str] = None
    filename: Optional[str] = None
    file_size: Optional[int] = None
    download_time: Optional[float] = None
    error_message: Optional[str] = None
    format_used: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'video_info': self.video_info.to_dict(),
            'success': self.success,
            'file_path': self.file_path,
            'filename': self.filename,
            'file_size': self.file_size,
            'download_time': self.download_time,
            'error_message': self.error_message,
            'format_used': self.format_used
        }
