
import yt_dlp
import os
import time
import random
from pathlib import Path
from typing import Dict, List, Optional
import logging
import requests
from urllib.parse import parse_qs, urlparse

class EnhancedYouTubeDownloader:
    def __init__(self, output_dir: str, quality: str = "best", format_type: str = "mp4"):
        self.output_dir = Path(output_dir)
        self.quality = quality
        self.format_type = format_type
        self.logger = logging.getLogger(__name__)
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # User agents to rotate
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent."""
        return random.choice(self.user_agents)
    
    def _add_random_delay(self, min_delay: float = 0.5, max_delay: float = 2.0):
        """Add random delay to avoid rate limiting."""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _get_ydl_opts(self, custom_opts: Optional[Dict] = None) -> Dict:
        """Get enhanced yt-dlp options with anti-detection measures."""
        
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
            
            # Enhanced options for bypassing restrictions
            'user_agent': self._get_random_user_agent(),
            'referer': 'https://www.youtube.com/',
            'headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip,deflate',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            
            # Retry and timeout settings
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            'keep_video': False,
            'no_warnings': False,
            
            # Bypass age restrictions
            'age_limit': 18,
            
            # Additional extraction options
            'extract_flat': False,
            'writeinfojson': False,
            'writedescription': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': True,
            
            # Network settings
            'socket_timeout': 30,
            'http_chunk_size': 10485760,  # 10MB chunks
            
            # Use cookies if available
            'cookiefile': None,
            'cookiesfrombrowser': None,
        }
        
        if custom_opts:
            base_opts.update(custom_opts)
        
        return base_opts
    
    def _validate_url(self, url: str) -> bool:
        """Validate YouTube URL accessibility."""
        try:
            # Simple HTTP check
            headers = {'User-Agent': self._get_random_user_agent()}
            response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
            return response.status_code == 200
        except:
            return True  # Assume valid if we can't check
    
    def download_video(self, url: str, retry_count: int = 3) -> Dict:
        """Download a single video with enhanced error handling."""
        
        for attempt in range(retry_count):
            try:
                self.logger.info(f"Attempting to download (attempt {attempt + 1}/{retry_count}): {url}")
                
                # Add random delay before each attempt
                if attempt > 0:
                    self._add_random_delay(1.0, 3.0)
                
                # Try different extraction strategies
                result = self._try_download_strategies(url)
                
                if result['success']:
                    return result
                else:
                    self.logger.warning(f"Download attempt {attempt + 1} failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                self.logger.error(f"Download attempt {attempt + 1} failed with exception: {str(e)}")
                if attempt == retry_count - 1:
                    return {
                        'success': False,
                        'error': f"All {retry_count} attempts failed. Last error: {str(e)}"
                    }
        
        return {
            'success': False,
            'error': f"Failed after {retry_count} attempts"
        }
    
    def _try_download_strategies(self, url: str) -> Dict:
        """Try different download strategies."""
        
        strategies = [
            self._strategy_standard,
            self._strategy_fallback_quality,
            self._strategy_audio_fallback,
            self._strategy_minimal_options
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                self.logger.info(f"Trying download strategy {i + 1}")
                result = strategy(url)
                if result['success']:
                    return result
            except Exception as e:
                self.logger.warning(f"Strategy {i + 1} failed: {str(e)}")
                continue
        
        return {'success': False, 'error': 'All download strategies failed'}
    
    def _strategy_standard(self, url: str) -> Dict:
        """Standard download strategy."""
        ydl_opts = self._get_ydl_opts()
        return self._execute_download(url, ydl_opts)
    
    def _strategy_fallback_quality(self, url: str) -> Dict:
        """Fallback to lower quality if original fails."""
        ydl_opts = self._get_ydl_opts()
        ydl_opts['format'] = 'worst[ext=mp4]/worst'
        return self._execute_download(url, ydl_opts)
    
    def _strategy_audio_fallback(self, url: str) -> Dict:
        """Fallback to audio-only download."""
        ydl_opts = self._get_ydl_opts()
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        return self._execute_download(url, ydl_opts)
    
    def _strategy_minimal_options(self, url: str) -> Dict:
        """Minimal options strategy for problematic videos."""
        ydl_opts = {
            'format': 'best',
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'ignoreerrors': True,
            'no_warnings': True,
            'user_agent': self._get_random_user_agent(),
        }
        return self._execute_download(url, ydl_opts)
    
    def _execute_download(self, url: str, ydl_opts: Dict) -> Dict:
        """Execute download with given options."""
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Extract info first
                self.logger.info("Extracting video information...")
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return {'success': False, 'error': 'Could not extract video information'}
                
                title = info.get('title', 'Unknown Title')
                video_id = info.get('id', 'unknown')
                
                self.logger.info(f"Video info extracted: {title}")
                
                # Now download
                self.logger.info("Starting download...")
                ydl.download([url])
                
                # Find the downloaded file
                downloaded_file = self._find_downloaded_file(title, video_id)
                
                if downloaded_file:
                    return {
                        'success': True,
                        'filename': downloaded_file.name,
                        'file_path': str(downloaded_file),
                        'title': title,
                        'duration': info.get('duration', 0),
                        'view_count': info.get('view_count', 0),
                        'video_id': video_id
                    }
                else:
                    return {'success': False, 'error': 'Download completed but file not found'}
                
            except yt_dlp.utils.DownloadError as e:
                error_msg = str(e)
                if "403" in error_msg:
                    return {'success': False, 'error': 'Video access forbidden (403). Video may be restricted or private.'}
                elif "404" in error_msg:
                    return {'success': False, 'error': 'Video not found (404). Video may have been deleted.'}
                else:
                    return {'success': False, 'error': f'Download error: {error_msg}'}
            
            except Exception as e:
                return {'success': False, 'error': f'Unexpected error: {str(e)}'}
    
    def _find_downloaded_file(self, title: str, video_id: str) -> Optional[Path]:
        """Enhanced file finding with multiple strategies."""
        
        # Strategy 1: Find by sanitized title
        clean_title = self._sanitize_for_search(title)
        for file_path in self.output_dir.iterdir():
            if file_path.is_file() and clean_title.lower() in file_path.stem.lower():
                return file_path
        
        # Strategy 2: Find by video ID
        for file_path in self.output_dir.iterdir():
            if file_path.is_file() and video_id in file_path.stem:
                return file_path
        
        # Strategy 3: Find most recent file
        valid_extensions = ['.mp4', '.webm', '.mp3', '.mkv', '.m4a', '.wav']
        recent_files = [
            f for f in self.output_dir.iterdir() 
            if f.is_file() and f.suffix.lower() in valid_extensions
        ]
        
        if recent_files:
            # Return the most recently modified file
            return max(recent_files, key=lambda x: x.stat().st_mtime)
        
        return None
    
    def _sanitize_for_search(self, title: str) -> str:
        """Sanitize title for file searching."""
        # Remove common problematic characters
        chars_to_remove = ['|', ':', '*', '?', '"', '<', '>', '/', '\\']
        for char in chars_to_remove:
            title = title.replace(char, '')
        
        # Replace multiple spaces with single space
        import re
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title
    
    def get_playlist_info(self, playlist_url: str) -> Dict:
        """Extract playlist information with enhanced error handling."""
        try:
            ydl_opts = self._get_ydl_opts()
            ydl_opts['extract_flat'] = True
            ydl_opts['quiet'] = True
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.logger.info("Extracting playlist information...")
                info = ydl.extract_info(playlist_url, download=False)
                
                if not info:
                    return {'success': False, 'error': 'Could not extract playlist information'}
                
                videos = []
                entries = info.get('entries', [])
                
                for entry in entries:
                    if entry and entry.get('id'):
                        videos.append({
                            'title': entry.get('title', 'Unknown Title'),
                            'url': entry.get('webpage_url', f"https://www.youtube.com/watch?v={entry['id']}"),
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
                'error': f'Playlist extraction failed: {str(e)}',
                'videos': []
            }
    
    def test_video_accessibility(self, url: str) -> Dict:
        """Test if a video is accessible before downloading."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'user_agent': self._get_random_user_agent(),
                'simulate': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info:
                    return {
                        'accessible': True,
                        'title': info.get('title', 'Unknown'),
                        'duration': info.get('duration', 0),
                        'upload_date': info.get('upload_date', ''),
                        'view_count': info.get('view_count', 0)
                    }
                else:
                    return {'accessible': False, 'error': 'No video information available'}
        
        except Exception as e:
            return {'accessible': False, 'error': str(e)}
