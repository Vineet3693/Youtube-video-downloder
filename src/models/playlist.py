
from dataclasses import dataclass
from typing import List, Dict, Optional
from .video import VideoInfo, DownloadResult

@dataclass
class PlaylistInfo:
    """Data model for playlist information."""
    
    id: str
    title: str
    url: str
    uploader: Optional[str] = None
    description: Optional[str] = None
    video_count: int = 0
    videos: List[VideoInfo] = None
    
    def __post_init__(self):
        if self.videos is None:
            self.videos = []
        if self.title:
            self.title = self._sanitize_title(self.title)
    
    def _sanitize_title(self, title: str) -> str:
        """Sanitize playlist title."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '_')
        return title.strip()
    
    def add_video(self, video_info: VideoInfo):
        """Add video to playlist."""
        self.videos.append(video_info)
        self.video_count = len(self.videos)
    
    def get_videos_slice(self, start: int = 0, end: Optional[int] = None) -> List[VideoInfo]:
        """Get a slice of videos from the playlist."""
        if end is None or end > len(self.videos):
            end = len(self.videos)
        return self.videos[start:end]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'uploader': self.uploader,
            'description': self.description,
            'video_count': self.video_count,
            'videos': [video.to_dict() for video in self.videos]
        }

@dataclass
class PlaylistDownloadResult:
    """Data model for playlist download results."""
    
    playlist_info: PlaylistInfo
    download_results: List[DownloadResult]
    total_requested: int
    total_successful: int
    total_failed: int
    zip_file_path: Optional[str] = None
    zip_file_size: Optional[int] = None
    total_download_time: Optional[float] = None
    
    def __post_init__(self):
        self.total_successful = sum(1 for result in self.download_results if result.success)
        self.total_failed = len(self.download_results) - self.total_successful
    
    def get_success_rate(self) -> float:
        """Get download success rate as percentage."""
        if not self.download_results:
            return 0.0
        return (self.total_successful / len(self.download_results)) * 100
    
    def get_failed_videos(self) -> List[DownloadResult]:
        """Get list of failed downloads."""
        return [result for result in self.download_results if not result.success]
    
    def get_successful_videos(self) -> List[DownloadResult]:
        """Get list of successful downloads."""
        return [result for result in self.download_results if result.success]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'playlist_info': self.playlist_info.to_dict(),
            'download_results': [result.to_dict() for result in self.download_results],
            'total_requested': self.total_requested,
            'total_successful': self.total_successful,
            'total_failed': self.total_failed,
            'zip_file_path': self.zip_file_path,
            'zip_file_size': self.zip_file_size,
            'total_download_time': self.total_download_time,
            'success_rate': self.get_success_rate()
        }
