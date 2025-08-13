
import streamlit as st
import os
import tempfile
import shutil
from pathlib import Path
import zipfile
import io
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.downloader.youtube_dl import EnhancedYouTubeDownloader
from src.utils.validators import URLValidator
from app.components.sidebar import render_sidebar
from app.components.download_form import render_download_form, show_url_examples
from app.components.progress_tracker import render_progress_display
from app.config import Config

def main():
    st.set_page_config(
        page_title="YouTube Downloader Pro",
        page_icon="🎥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'download_count' not in st.session_state:
        st.session_state.download_count = 0
    if 'success_count' not in st.session_state:
        st.session_state.success_count = 0
    if 'error_history' not in st.session_state:
        st.session_state.error_history = []
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #ff4b4b;
        margin-bottom: 30px;
        font-size: 2.5rem;
        font-weight: 600;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='main-header'>🎥 YouTube Downloader Pro</h1>", unsafe_allow_html=True)
    
    # Sidebar with settings
    settings = render_sidebar()
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["🎬 Single Video", "📋 Playlist", "📊 Statistics", "❓ Help"])
    
    with tab1:
        render_single_video_tab(settings)
    
    with tab2:
        render_playlist_tab(settings)
    
    with tab3:
        render_statistics_tab()
    
    with tab4:
        render_help_tab()

def render_single_video_tab(settings):
    st.subheader("🎬 Single Video Download")
    
    # Show URL examples
    show_url_examples()
    
    url, submitted, options = render_download_form("single")
    
    if submitted and url:
        if URLValidator.is_valid_youtube_url(url):
            # Test video accessibility first
            with st.spinner("🔍 Checking video accessibility..."):
                downloader = EnhancedYouTubeDownloader(
                    tempfile.gettempdir(),
                    settings['quality'],
                    settings['format_type']
                )
                
                access_test = downloader.test_video_accessibility(url)
                
                if access_test['accessible']:
                    st.success(f"✅ Video accessible: {access_test['title']}")
                    download_single_video(url, settings)
                else:
                    st.error(f"❌ Video not accessible: {access_test['error']}")
                    st.info("💡 This could be due to:")
                    st.markdown("""
                    - Video is private or restricted
                    - Video has been deleted
                    - Geographic restrictions
                    - Age restrictions
                    - Copyright restrictions
                    
                    Try a different video or check the URL.
                    """)
        else:
            st.error("❌ Invalid YouTube URL. Please check and try again.")

def download_single_video(url, settings):
    progress_container = st.container()
    status_container = st.container()
    result_container = st.container()
    
    with status_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        info_text = st.empty()
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = EnhancedYouTubeDownloader(
                temp_dir, 
                settings['quality'], 
                settings['format_type']
            )
            
            # Update progress
            status_text.text("🔄 Initializing download...")
            info_text.info("Using enhanced downloader with anti-restriction measures")
            progress_bar.progress(10)
            
            # Attempt download with progress updates
            result = download_with_progress_updates(
                downloader, url, progress_bar, status_text, info_text
            )
            
            if result['success']:
                # Success handling
                st.session_state.download_count += 1
                st.session_state.success_count += 1
                
                with result_container:
                    st.success("✅ Download completed successfully!")
                    
                    # Show file info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("File Size", get_file_size_mb(result['file_path']))
                    with col2:
                        st.metric("Duration", format_duration(result.get('duration', 0)))
                    with col3:
                        st.metric("Quality", settings['quality'])
                    
                    # Download button
                    file_path = result['file_path']
                    filename = result['filename']
                    
                    with open(file_path, "rb") as file:
                        st.download_button(
                            label=f"⬇️ Download {filename}",
                            data=file.read(),
                            file_name=filename,
                            mime=get_mime_type(settings['format_type']),
                            key=f"download_{int(time.time())}"
                        )
            else:
                # Error handling
                st.session_state.download_count += 1
                st.session_state.error_history.append({
                    'url': url,
                    'error': result['error'],
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'settings': settings.copy()
                })
                
                with result_container:
                    st.error(f"❌ Download failed: {result['error']}")
                    
                    # Show troubleshooting suggestions
                    show_troubleshooting_suggestions(result['error'])
                    
    except Exception as e:
        logger.error(f"Unexpected error in download_single_video: {str(e)}")
        st.error(f"❌ An unexpected error occurred: {str(e)}")

def download_with_progress_updates(downloader, url, progress_bar, status_text, info_text):
    """Download with detailed progress updates."""
    
    try:
        # Phase 1: Video info extraction
        status_text.text("🔍 Extracting video information...")
        progress_bar.progress(20)
        
        # Phase 2: Format selection
        status_text.text("⚙️ Selecting optimal format...")
        info_text.info("Choosing best available quality and format")
        progress_bar.progress(40)
        
        # Phase 3: Download attempt
        status_text.text("⬇️ Starting download...")
        info_text.info("Using enhanced downloader with multiple fallback strategies")
        progress_bar.progress(60)
        
        # Actual download
        result = downloader.download_video(url)
        
        if result['success']:
            status_text.text("✅ Download completed!")
            progress_bar.progress(100)
            info_text.success(f"Successfully downloaded: {result['filename']}")
        else:
            status_text.text("❌ Download failed")
            progress_bar.progress(100)
            info_text.error(f"Error: {result['error']}")
        
        return result
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def show_troubleshooting_suggestions(error_message):
    """Show context-specific troubleshooting suggestions."""
    
    st.subheader("🔧 Troubleshooting Suggestions")
    
    if "403" in error_message or "Forbidden" in error_message:
        st.warning("""
        **403 Forbidden Error - Common Solutions:**
        
        1. **Try a different quality:** Switch to 480p or 360p
        2. **Use audio-only mode:** Select MP3 format 
        3. **Wait and retry:** YouTube may be temporarily blocking requests
        4. **Check video privacy:** Make sure the video is public
        5. **Try a different video:** Some videos have stricter protection
        """)
        
        # Offer retry with different settings
        if st.button("🔄 Retry with Lower Quality"):
            st.rerun()
            
    elif "404" in error_message or "not found" in error_message:
        st.warning("""
        **Video Not Found - Possible Causes:**
        
        1. **Video was deleted** by the uploader
        2. **Incorrect URL** - double-check the link
        3. **Video is private** or unlisted
        4. **Regional restrictions** may apply
        """)
        
    elif "timeout" in error_message.lower():
        st.warning("""
        **Timeout Error - Solutions:**
        
        1. **Check internet connection**
        2. **Retry the download** - temporary network issue
        3. **Try during off-peak hours**
        4. **Use a VPN** if regional issues suspected
        """)
        
    else:
        st.info("""
        **General Troubleshooting:**
        
        1. **Verify the URL** is correct and complete
        2. **Try different quality settings**
        3. **Switch to audio-only** if video fails
        4. **Wait a few minutes** and try again
        5. **Check if video requires sign-in**
        """)

def render_playlist_tab(settings):
    st.subheader("📋 Playlist Download")
    
    playlist_url, submitted, options = render_download_form("playlist")
    
    if submitted and playlist_url:
        if URLValidator.is_valid_youtube_playlist_url(playlist_url):
            download_playlist(playlist_url, settings, options)
        else:
            st.error("❌ Invalid YouTube playlist URL. Please check and try again.")

def download_playlist(playlist_url, settings, options):
    progress_container = st.container()
    status_container = st.container()
    
    with status_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        playlist_info = st.empty()
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = EnhancedYouTubeDownloader(
                temp_dir,
                settings['quality'],
                settings['format_type']
            )
            
            # Extract playlist info
            status_text.text("🔄 Fetching playlist information...")
            progress_bar.progress(5)
            
            playlist_data = downloader.get_playlist_info(playlist_url)
            
            if not playlist_data['success']:
                st.error(f"❌ Failed to fetch playlist: {playlist_data['error']}")
                return
            
            videos = playlist_data['videos']
            total_videos = len(videos)
            
            # Apply filters
            start_idx = max(0, options.get('start_index', 1) - 1)
            end_idx = min(total_videos, options.get('end_index', total_videos) or total_videos)
            max_videos = min(options.get('max_videos', 50), 50)  # Limit to 50 for performance
            
            filtered_videos = videos[start_idx:end_idx][:max_videos]
            
            playlist_info.info(f"📋 Playlist: {playlist_data['title']} ({len(filtered_videos)} videos selected)")
            
            # Download videos
            successful_downloads = []
            failed_downloads = []
            
            for i, video in enumerate(filtered_videos):
                progress = int((i / len(filtered_videos)) * 90) + 5
                progress_bar.progress(progress)
                status_text.text(f"⬇️ Downloading {i+1}/{len(filtered_videos)}: {video['title'][:50]}...")
                
                try:
                    result = downloader.download_video(video['url'])
                    if result['success']:
                        successful_downloads.append(result)
                    else:
                        failed_downloads.append({'video': video, 'error': result['error']})
                        
                    # Add small delay between downloads
                    time.sleep(0.5)
                    
                except Exception as e:
                    failed_downloads.append({'video': video, 'error': str(e)})
            
            progress_bar.progress(95)
            status_text.text("📦 Creating download package...")
            
            # Create ZIP file
            if successful_downloads:
                zip_buffer = create_playlist_zip(successful_downloads, playlist_data['title'])
                
                progress_bar.progress(100)
                status_text.text("✅ Playlist download completed!")
                
                # Show results
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ Successful", len(successful_downloads))
                with col2:
                    st.metric("❌ Failed", len(failed_downloads))
                with col3:
                    success_rate = (len(successful_downloads) / len(filtered_videos)) * 100
                    st.metric("Success Rate", f"{success_rate:.1f}%")
                
                # Download button
                st.download_button(
                    label=f"⬇️ Download Playlist ZIP ({len(successful_downloads)} videos)",
                    data=zip_buffer.getvalue(),
                    file_name=f"{playlist_data['title']}.zip",
                    mime="application/zip",
                    key=f"playlist_{int(time.time())}"
                )
                
                # Show failed downloads
                if failed_downloads:
                    with st.expander(f"❌ Failed Downloads ({len(failed_downloads)})"):
                        for failed in failed_downloads:
                            st.error(f"**{failed['video']['title']}**: {failed['error']}")
            else:
                st.error("❌ No videos were successfully downloaded from the playlist.")
                
    except Exception as e:
        logger.error(f"Playlist download error: {str(e)}")
        st.error(f"❌ Playlist download failed: {str(e)}")

def create_playlist_zip(successful_downloads, playlist_title):
    """Create ZIP file from successful downloads."""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, download in enumerate(successful_downloads):
            file_path = download['file_path']
            filename = download['filename']
            
            # Add file to ZIP with index prefix for ordering
            zip_filename = f"{i+1:03d}_{filename}"
            zip_file.write(file_path, zip_filename)
    
    zip_buffer.seek(0)
    return zip_buffer

def render_statistics_tab():
    st.subheader("📊 Download Statistics")
    
    if st.session_state.download_count == 0:
        st.info("📈 No downloads yet. Start downloading to see statistics!")
        return
    
    # Overall stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Downloads", st.session_state.download_count)
    
    with col2:
        st.metric("Successful", st.session_state.success_count)
    
    with col3:
        failed_count = st.session_state.download_count - st.session_state.success_count
        st.metric("Failed", failed_count)
    
    with col4:
        if st.session_state.download_count > 0:
            success_rate = (st.session_state.success_count / st.session_state.download_count) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
    
    # Error history
    if st.session_state.error_history:
        st.subheader("🔍 Recent Errors")
        
        for i, error in enumerate(reversed(st.session_state.error_history[-10:])):  # Show last 10 errors
            with st.expander(f"Error {len(st.session_state.error_history) - i}: {error['timestamp']}"):
                st.text(f"URL: {error['url']}")
                st.text(f"Error: {error['error']}")
                st.text(f"Settings: Quality: {error['settings']['quality']}, Format: {error['settings']['format_type']}")
    
    # Clear statistics
    if st.button("🗑️ Clear Statistics"):
        st.session_state.download_count = 0
        st.session_state.success_count = 0
        st.session_state.error_history = []
        st.success("Statistics cleared!")
        st.rerun()

def render_help_tab():
    st.subheader("❓ Help & FAQ")
    
    # Common issues
    st.markdown("### 🔧 Common Issues & Solutions")
    
    with st.expander("🚫 HTTP 403 Forbidden Error"):
        st.markdown("""
        **This is the most common error. Here's how to fix it:**
        
        1. **Lower the quality**: Try 480p or 360p instead of 1080p
        2. **Switch to audio-only**: Select MP3 format 
        3. **Wait and retry**: YouTube temporarily blocks some requests
        4. **Different video**: Some videos have enhanced protection
        
        **Why this happens:**
        - YouTube's anti-bot measures
        - Video has restricted access
        - Too many recent requests from your IP
        """)
    
    with st.expander("🔍 Video Not Found (404)"):
        st.markdown("""
        **Possible reasons:**
        
        - Video was deleted or made private
        - Incorrect URL format
        - Regional restrictions
        - Age-restricted content
        
        **Solutions:**
        - Double-check the URL
        - Try accessing the video in your browser first
        - Use a VPN if regional restrictions apply
        """)
    
    with st.expander("⏱️ Timeout Errors"):
        st.markdown("""
        **Network-related issues:**
        
        - Slow internet connection
        - YouTube server issues
        - Large file size
        
        **Solutions:**
        - Check your internet connection
        - Try during off-peak hours
        - Lower video quality
        - Retry after a few minutes
        """)
    
    # Supported formats
    st.markdown("### 📁 Supported Formats")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Video Formats:**
        - MP4 (recommended)
        - WebM
        - MKV (when available)
        """)
    
    with col2:
        st.markdown("""
        **Audio Formats:**
        - MP3 (192 kbps)
        - M4A (when available)
        - WAV (when available)
        """)
    
    # Quality options
    st.markdown("### 🎥 Quality Options")
    
    quality_info = {
        "best": "Highest available quality (may be very large)",
        "1080p": "Full HD - good balance of quality and size",
        "720p": "HD - recommended for most users",
        "480p": "Standard quality - smaller files",
        "360p": "Low quality - smallest files, good for slow connections",
        "worst": "Lowest available quality"
    }
    
    for quality, description in quality_info.items():
        st.write(f"**{quality}**: {description}")
    
    # Tips for better downloads
    st.markdown("### 💡 Tips for Better Downloads")
    
    st.info("""
    **For best results:**
    
    1. **Start with 720p quality** - good balance of quality and reliability
    2. **Use MP4 format** - most compatible and reliable
    3. **Try audio-only** if video downloads fail
    4. **Avoid peak hours** (evening in your timezone)
    5. **Check video accessibility** in your browser first
    6. **For playlists**: Limit to 20-30 videos at a time
    7. **Clear browser cache** if experiencing persistent issues
    """)
    
    # Legal disclaimer
    st.markdown("### ⚖️ Legal Notice")
    
    st.warning("""
    **Important Legal Information:**
    
    - Only download content you have permission to download
    - Respect copyright laws and YouTube's Terms of Service
    - This tool is for personal use only
    - Do not redistribute downloaded content without permission
    - Some content may be protected by copyright
    
    **Use this tool responsibly and ethically.**
    """)
    
    # Contact information
    st.markdown("### 📞 Support")
    
    st.info("""
    **Need help?**
    
    - Check the FAQ above first
    - Report issues on GitHub: [GitHub Issues](https://github.com/yourusername/youtube-downloader-app/issues)
    - Read the documentation: [User Guide](https://github.com/yourusername/youtube-downloader-app/docs)
    """)

# Utility functions
def get_file_size_mb(file_path):
    """Get file size in MB."""
    try:
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.1f} MB"
    except:
        return "Unknown"

def format_duration(seconds):
    """Format duration in seconds to readable string."""
    if not seconds:
        return "Unknown"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    else:
        return f"{int(minutes):02d}:{int(seconds):02d}"

def get_mime_type(format_type):
    """Get MIME type for download."""
    mime_types = {
        'mp4': 'video/mp4',
        'webm': 'video/webm',
        'mp3 (audio only)': 'audio/mpeg'
    }
    return mime_types.get(format_type, 'application/octet-stream')

if __name__ == "__main__":
    main()
