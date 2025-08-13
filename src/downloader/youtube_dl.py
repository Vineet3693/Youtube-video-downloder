
import yt_dlp
import os
from pathlib import Path
from typing import Dict, List, Optional
import logging

class YouTubeDownloader:
    def __init__(self, output_dir: str, quality: str = "best", format_type: str = "mp4"):
        self.output_dir = Path(output_dir)
        self.quality = quality
        self.format_type = format_type
        self.logger = logging.getLogger(__name__)
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_ydl_opts(self, custom_opts: Optional[Dict] = None) -> Dict:
        """Get yt-dlp options based on current settings."""
        
        # Format selection based on quality and type
        if self.format_type == "mp3 (audio only)":
            format_selector = "bestaudio/best"
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            if self.quality == "best":
                format_selector = f"best[ext={self.format_type}]/best"
            elif self.quality == "worst":
                format_selector = f"worst[ext={self.format_type}]/worst"
            else:
                height = self.quality.replace('p', '')
                format_selector = f"best[height<={height}][ext={self.format_type}]/best[height<={height}]/best"
            postprocessors = []
        
        base_opts = {
            'format': format_selector,
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'postprocessors': postprocessors,
            'writeinfojson': False,
            'writedescription': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': True,
            'no_warnings': True,
        }
        
        if custom_opts:
            base_opts.update(custom_opts)
        
        return base_opts
    
    def download_video(self, url: str) -> Dict:
        """Download a single video."""
        try:
            ydl_opts = self._get_ydl_opts()
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(url, download=False)
                filename = ydl.prepare_filename(info)
                
                # Download the video
                ydl.download([url])
                
                # Find the actual downloaded file
                actual_file = self._find_downloaded_file(info['title'])
                
                return {
                    'success': True,
                    'filename': os.path.basename(actual_file),
                    'file_path': actual_file,
                    'title': info['title'],
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0)
                }
        
        except Exception as e:
            self.logger.error(f"Error downloading video {url}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_playlist_info(self, playlist_url: str) -> Dict:
        """Extract playlist information."""
        try:
            ydl_opts = self._get_ydl_opts()
            ydl_opts['extract_flat'] = True
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
                
                videos = []
                for entry in info.get('entries', []):
                  if entry:
                        videos.append({
                            'title': entry.get('title', 'Unknown'),
                            'url': entry.get('url', ''),
                            'duration': entry.get('duration', 0),
                            'id': entry.get('id', '')
                        })
                
                return {
                    'success': True,
                    'title': info.get('title', 'Unknown Playlist'),
                    'videos': videos,
                    'total_count': len(videos)
                }
        
        except Exception as e:
            self.logger.error(f"Error extracting playlist info {playlist_url}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'videos': []
            }
    
    def _find_downloaded_file(self, title: str) -> str:
        """Find the downloaded file in the output directory."""
        # Clean title for filename matching
        clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        for file_path in self.output_dir.iterdir():
            if file_path.is_file() and clean_title.lower() in file_path.stem.lower():
                return str(file_path)
        
        # If not found by title matching, return the most recent file
        files = [f for f in self.output_dir.iterdir() if f.is_file()]
        if files:
            return str(max(files, key=os.path.getctime))
        
        raise FileNotFoundError(f"Downloaded file not found for title: {title}")
