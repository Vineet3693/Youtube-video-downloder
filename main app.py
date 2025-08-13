
import streamlit as st
import os
import tempfile
import shutil
from pathlib import Path
import zipfile
import io

from src.downloader.youtube_dl import YouTubeDownloader
from src.utils.validators import URLValidator
from app.components.download_form import render_download_form
from app.components.progress_tracker import ProgressTracker
from app.config import Config

def main():
    st.set_page_config(
        page_title="YouTube Downloader",
        page_icon="🎥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #ff4b4b;
        margin-bottom: 30px;
    }
    .download-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='main-header'>🎥 YouTube Video & Playlist Downloader</h1>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        quality = st.selectbox(
            "Video Quality",
            ["best", "1080p", "720p", "480p", "360p", "worst"],
            index=0
        )
        
        format_type = st.selectbox(
            "Download Format",
            ["mp4", "webm", "mp3 (audio only)"],
            index=0
        )
        
        max_downloads = st.slider("Max Concurrent Downloads", 1, 5, 2)
        
        st.markdown("---")
        st.markdown("### 📚 Supported Platforms")
        st.markdown("- YouTube Videos\n- YouTube Playlists\n- YouTube Shorts")
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["🎬 Single Video", "📋 Playlist", "📊 History"])
    
    with tab1:
        render_single_video_downloader(quality, format_type)
    
    with tab2:
        render_playlist_downloader(quality, format_type, max_downloads)
    
    with tab3:
        render_download_history()

def render_single_video_downloader(quality, format_type):
    st.subheader("Download Single Video")
    
    with st.form("single_video_form"):
        url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
        col1, col2 = st.columns([3, 1])
        
        with col2:
            submitted = st.form_submit_button("Download", type="primary", use_container_width=True)
        
        if submitted and url:
            if URLValidator.is_valid_youtube_url(url):
                download_single_video(url, quality, format_type)
            else:
                st.error("❌ Invalid YouTube URL. Please check and try again.")

def render_playlist_downloader(quality, format_type, max_downloads):
    st.subheader("Download Playlist")
    
    with st.form("playlist_form"):
        playlist_url = st.text_input("YouTube Playlist URL", placeholder="https://www.youtube.com/playlist?list=...")
        
        col1, col2 = st.columns(2)
        with col1:
            start_index = st.number_input("Start from video #", min_value=1, value=1)
        with col2:
            end_index = st.number_input("End at video # (0 for all)", min_value=0, value=0)
        
        submitted = st.form_submit_button("Download Playlist", type="primary", use_container_width=True)
        
        if submitted and playlist_url:
            if URLValidator.is_valid_youtube_playlist_url(playlist_url):
                download_playlist(playlist_url, quality, format_type, start_index, end_index, max_downloads)
            else:
                st.error("❌ Invalid YouTube playlist URL. Please check and try again.")

def download_single_video(url, quality, format_type):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = YouTubeDownloader(temp_dir, quality, format_type)
            
            # Download video
            status_text.text("🔄 Initializing download...")
            progress_bar.progress(25)
            
            result = downloader.download_video(url)
            progress_bar.progress(75)
            
            if result['success']:
                status_text.text("✅ Download completed successfully!")
                progress_bar.progress(100)
                
                # Provide download link
                file_path = result['file_path']
                file_name = result['filename']
                
                with open(file_path, "rb") as file:
                    st.download_button(
                        label=f"⬇️ Download {file_name}",
                        data=file,
                        file_name=file_name,
                        mime=get_mime_type(format_type)
                    )
            else:
                st.error(f"❌ Download failed: {result['error']}")
                
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")

def download_playlist(playlist_url, quality, format_type, start_index, end_index, max_downloads):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = YouTubeDownloader(temp_dir, quality, format_type)
            
            status_text.text("🔄 Fetching playlist information...")
            progress_bar.progress(10)
            
            playlist_info = downloader.get_playlist_info(playlist_url)
            total_videos = len(playlist_info['videos'])
            
            if end_index == 0:
                end_index = total_videos
            
            videos_to_download = playlist_info['videos'][start_index-1:end_index]
            
            status_text.text(f"📥 Downloading {len(videos_to_download)} videos...")
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for i, video_info in enumerate(videos_to_download):
                    progress = int((i / len(videos_to_download)) * 80) + 10
                    progress_bar.progress(progress)
                    status_text.text(f"⬇️ Downloading: {video_info['title'][:50]}...")
                    
                    result = downloader.download_video(video_info['url'])
                    if result['success']:
                        zip_file.write(result['file_path'], result['filename'])
            
            progress_bar.progress(100)
            status_text.text("✅ Playlist download completed!")
            
            zip_buffer.seek(0)
            st.download_button(
                label=f"⬇️ Download Playlist ZIP ({len(videos_to_download)} videos)",
                data=zip_buffer.getvalue(),
                file_name=f"{playlist_info['title']}.zip",
                mime="application/zip"
            )
            
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")

def render_download_history():
    st.subheader("📊 Download History")
    st.info("Download history feature will be implemented in future versions.")

def get_mime_type(format_type):
    mime_types = {
        'mp4': 'video/mp4',
        'webm': 'video/webm',
        'mp3 (audio only)': 'audio/mpeg'
    }
    return mime_types.get(format_type, 'application/octet-stream')

if __name__ == "__main__":
    main()
