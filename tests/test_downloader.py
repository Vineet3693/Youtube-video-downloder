
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.downloader.youtube_dl import YouTubeDownloader
from src.utils.validators import URLValidator

class TestYouTubeDownloader(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = YouTubeDownloader(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        self.assertEqual(str(self.downloader.output_dir), self.temp_dir)
        self.assertEqual(self.downloader.quality, "best")
        self.assertEqual(self.downloader.format_type, "mp4")
    
    def test_get_ydl_opts_video(self):
        opts = self.downloader._get_ydl_opts()
        self.assertIn('format', opts)
        self.assertIn('outtmpl', opts)
        self.assertEqual(opts['format'], 'best[ext=mp4]/best')
    
    def test_get_ydl_opts_audio(self):
        downloader = YouTubeDownloader(self.temp_dir, format_type="mp3 (audio only)")
        opts = downloader._get_ydl_opts()
        self.assertEqual(opts['format'], 'bestaudio/best')
        self.assertTrue(len(opts['postprocessors']) > 0)
    
    @patch('yt_dlp.YoutubeDL')
    def test_download_video_success(self, mock_ydl_class):
        # Mock yt-dlp behavior
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        mock_info = {
            'title': 'Test Video',
            'duration': 120,
            'view_count': 1000
        }
        mock_ydl.extract_info.return_value = mock_info
        mock_ydl.prepare_filename.return_value = 'Test Video.mp4'
        
        # Create a dummy file to simulate download
        test_file = Path(self.temp_dir) / 'Test Video.mp4'
        test_file.touch()
        
        result = self.downloader.download_video('https://www.youtube.com/watch?v=test123')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['title'], 'Test Video')
        self.assertIn('filename', result)
    
    @patch('yt_dlp.YoutubeDL')
    def test_get_playlist_info(self, mock_ydl_class):
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        mock_playlist_info = {
            'title': 'Test Playlist',
            'entries': [
                {'title': 'Video 1', 'url': 'https://youtube.com/watch?v=1', 'id': '1'},
                {'title': 'Video 2', 'url': 'https://youtube.com/watch?v=2', 'id': '2'}
            ]
        }
        mock_ydl.extract_info.return_value = mock_playlist_info
        
        result = self.downloader.get_playlist_info('https://youtube.com/playlist?list=test')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['title'], 'Test Playlist')
        self.assertEqual(len(result['videos']), 2)

class TestURLValidator(unittest.TestCase):
    
    def test_valid_youtube_urls(self):
        valid_urls = [
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'https://youtu.be/dQw4w9WgXcQ',
            'https://www.youtube.com/shorts/dQw4w9WgXcQ',
            'youtube.com/watch?v=dQw4w9WgXcQ'
        ]
        
        for url in valid_urls:
            self.assertTrue(URLValidator.is_valid_youtube_url(url))
    
    def test_invalid_youtube_urls(self):
        invalid_urls = [
            'https://vimeo.com/123456',
            'https://facebook.com/video',
            'invalid-url',
            '',
            'https://youtube.com/invalid'
        ]
        
        for url in invalid_urls:
            self.assertFalse(URLValidator.is_valid_youtube_url(url))
    
    def test_valid_playlist_urls(self):
        valid_urls = [
            'https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMekEYPUOJjkUaO04',
            'https://youtube.com/watch?v=abc123&list=PLrAXtmRdnEQy6nuLMekEYPUOJjkUaO04'
        ]
        
        for url in valid_urls:
            self.assertTrue(URLValidator.is_valid_youtube_playlist_url(url))
    
    def test_extract_video_id(self):
        url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        video_id = URLValidator.extract_video_id(url)
        self.assertEqual(video_id, 'dQw4w9WgXcQ')

if __name__ == '__main__':
    unittest.main()
