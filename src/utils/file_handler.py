
import os
import shutil
import zipfile
from pathlib import Path
from typing import List, Optional, Dict
import tempfile
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FileHandler:
    """Handles file operations for downloaded content."""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(tempfile.gettempdir()) / "youtube_downloads"
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def create_temp_dir(self, prefix: str = "download_") -> Path:
        """Create a temporary directory for downloads."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = self.base_dir / f"{prefix}{timestamp}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir
    
    def cleanup_temp_dir(self, temp_dir: Path):
        """Clean up temporary directory."""
        try:
            if temp_dir.exists() and temp_dir.is_dir():
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up temp directory {temp_dir}: {e}")
    
    def create_zip_from_files(self, files: List[Path], zip_name: str, temp_dir: Path) -> Path:
        """Create a ZIP file from a list of files."""
        zip_path = temp_dir / f"{zip_name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files:
                if file_path.exists():
                    # Use just the filename in the ZIP
                    zipf.write(file_path, file_path.name)
                    logger.info(f"Added {file_path.name} to ZIP")
        
        return zip_path
    
    def get_file_size(self, file_path: Path) -> str:
        """Get human-readable file size."""
        if not file_path.exists():
            return "Unknown"
        
        size = file_path.stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage."""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200-len(ext)] + ext
        
        return filename.strip()
    
    def find_downloaded_files(self, directory: Path, extensions: List[str] = None) -> List[Path]:
        """Find downloaded files in directory."""
        if extensions is None:
            extensions = ['.mp4', '.webm', '.mp3', '.mkv', '.avi']
        
        files = []
        for ext in extensions:
            files.extend(directory.glob(f"*{ext}"))
        
        return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
    
    def get_download_info(self, file_path: Path) -> Dict[str, str]:
        """Get information about downloaded file."""
        if not file_path.exists():
            return {}
        
        stat = file_path.stat()
        return {
            'filename': file_path.name,
            'size': self.get_file_size(file_path),
            'created': datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            'extension': file_path.suffix.lower()
        }
