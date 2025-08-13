
import streamlit as st
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from threading import Lock

@dataclass
class DownloadProgress:
    video_id: str
    title: str
    status: str  # 'pending', 'downloading', 'completed', 'failed'
    progress: float  # 0.0 to 1.0
    speed: str
    eta: str
    file_size: str
    error_message: Optional[str] = None

class ProgressTracker:
    def __init__(self):
        self.downloads: Dict[str, DownloadProgress] = {}
        self.lock = Lock()
    
    def add_download(self, video_id: str, title: str):
        """Add a new download to track."""
        with self.lock:
            self.downloads[video_id] = DownloadProgress(
                video_id=video_id,
                title=title,
                status='pending',
                progress=0.0,
                speed='',
                eta='',
                file_size=''
            )
    
    def update_progress(self, video_id: str, progress: float, speed: str = '', eta: str = '', file_size: str = ''):
        """Update download progress."""
        with self.lock:
            if video_id in self.downloads:
                self.downloads[video_id].progress = progress
                self.downloads[video_id].speed = speed
                self.downloads[video_id].eta = eta
                self.downloads[video_id].file_size = file_size
                
                if progress > 0:
                    self.downloads[video_id].status = 'downloading'
    
    def mark_completed(self, video_id: str):
        """Mark download as completed."""
        with self.lock:
            if video_id in self.downloads:
                self.downloads[video_id].status = 'completed'
                self.downloads[video_id].progress = 1.0
    
    def mark_failed(self, video_id: str, error_message: str):
        """Mark download as failed."""
        with self.lock:
            if video_id in self.downloads:
                self.downloads[video_id].status = 'failed'
                self.downloads[video_id].error_message = error_message
    
    def get_all_downloads(self) -> List[DownloadProgress]:
        """Get all downloads."""
        with self.lock:
            return list(self.downloads.values())
    
    def clear_completed(self):
        """Clear completed downloads."""
        with self.lock:
            self.downloads = {k: v for k, v in self.downloads.items() if v.status != 'completed'}
    
    def get_summary(self) -> Dict[str, int]:
        """Get download summary statistics."""
        with self.lock:
            summary = {'pending': 0, 'downloading': 0, 'completed': 0, 'failed': 0}
            for download in self.downloads.values():
                summary[download.status] += 1
            return summary

def render_progress_display(tracker: ProgressTracker, container=None):
    """Render progress display for downloads."""
    
    if container is None:
        container = st.container()
    
    downloads = tracker.get_all_downloads()
    
    if not downloads:
        return
    
    with container:
        st.subheader("📊 Download Progress")
        
        # Summary statistics
        summary = tracker.get_summary()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("⏳ Pending", summary['pending'])
        with col2:
            st.metric("⬇️ Downloading", summary['downloading'])
        with col3:
            st.metric("✅ Completed", summary['completed'])
        with col4:
            st.metric("❌ Failed", summary['failed'])
        
        # Individual download progress
        for download in downloads:
            render_single_progress(download)
        
        # Clear completed button
        if summary['completed'] > 0:
            if st.button("🗑️ Clear Completed", key="clear_completed"):
                tracker.clear_completed()
                st.rerun()

def render_single_progress(download: DownloadProgress):
    """Render progress for a single download."""
    
    with st.expander(f"{get_status_emoji(download.status)} {download.title[:50]}{'...' if len(download.title) > 50 else ''}", expanded=download.status == 'downloading'):
        
        # Progress bar
        if download.status in ['downloading', 'completed']:
            st.progress(download.progress)
            
            # Download info
            col1, col2, col3 = st.columns(3)
            with col1:
                if download.speed:
                    st.text(f"Speed: {download.speed}")
            with col2:
                if download.eta:
                    st.text(f"ETA: {download.eta}")
            with col3:
                if download.file_size:
                    st.text(f"Size: {download.file_size}")
        
        # Error message
        if download.status == 'failed' and download.error_message:
            st.error(f"Error: {download.error_message}")
        
        # Status
        st.text(f"Status: {download.status.title()}")

def get_status_emoji(status: str) -> str:
    """Get emoji for download status."""
    emojis = {
        'pending': '⏳',
        'downloading': '⬇️',
        'completed': '✅',
        'failed': '❌'
    }
    return emojis.get(status, '❓')

# Initialize global progress tracker
if 'progress_tracker' not in st.session_state:
    st.session_state.progress_tracker = ProgressTracker()
