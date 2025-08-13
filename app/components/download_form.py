
import streamlit as st
import re
from typing import Optional, Tuple
from src.utils.validators import URLValidator

def render_download_form(form_type: str = "single") -> Tuple[Optional[str], bool, dict]:
    """
    Render download form for single video or playlist.
    
    Args:
        form_type: "single" or "playlist"
        
    Returns:
        Tuple of (url, submitted, additional_options)
    """
    
    if form_type == "single":
        return _render_single_video_form()
    else:
        return _render_playlist_form()

def _render_single_video_form() -> Tuple[Optional[str], bool, dict]:
    """Render single video download form."""
    
    st.subheader("🎬 Single Video Download")
    
    with st.form("single_video_form", clear_on_submit=False):
        # URL Input with validation
        url = st.text_input(
            "YouTube Video URL",
            placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            help="Paste the YouTube video URL here"
        )
        
        # Preview section
        if url and URLValidator.is_valid_youtube_url(url):
            video_id = URLValidator.extract_video_id(url)
            if video_id:
                st.success("✅ Valid YouTube URL detected")
                
                # Show video thumbnail
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                try:
                    st.image(thumbnail_url, width=300, caption="Video Preview")
                except:
                    st.info("📹 Video preview unavailable")
        
        elif url:
            st.error("❌ Invalid YouTube URL. Please check the URL format.")
        
        # Submit button
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            submitted = st.form_submit_button(
                "🚀 Download",
                type="primary",
                use_container_width=True
            )
    
    additional_options = {}
    
    return url, submitted, additional_options

def _render_playlist_form() -> Tuple[Optional[str], bool, dict]:
    """Render playlist download form."""
    
    st.subheader("📋 Playlist Download")
    
    with st.form("playlist_form", clear_on_submit=False):
        # URL Input
        playlist_url = st.text_input(
            "YouTube Playlist URL",
            placeholder="https://www.youtube.com/playlist?list=PLrAXtmRdnEQy...",
            help="Paste the YouTube playlist URL here"
        )
        
        # Validation
        if playlist_url and URLValidator.is_valid_youtube_playlist_url(playlist_url):
            st.success("✅ Valid YouTube playlist URL detected")
        elif playlist_url:
            st.error("❌ Invalid playlist URL. Make sure it's a YouTube playlist.")
        
        # Range Selection
        st.subheader("📊 Download Range")
        col1, col2 = st.columns(2)
        
        with col1:
            start_index = st.number_input(
                "Start from video #",
                min_value=1,
                value=1,
                help="First video to download (1 = first video)"
            )
        
        with col2:
            end_index = st.number_input(
                "End at video #",
                min_value=0,
                value=0,
                help="Last video to download (0 = all videos)"
            )
        
        # Additional Options
        with st.expander("🔧 Playlist Options"):
            reverse_order = st.checkbox(
                "Download in reverse order",
                help="Download from newest to oldest"
            )
            
            skip_unavailable = st.checkbox(
                "Skip unavailable videos",
                value=True,
                help="Continue downloading even if some videos fail"
            )
            
            max_videos = st.slider(
                "Maximum videos to download",
                min_value=1,
                max_value=100,
                value=50,
                help="Limit the number of videos to download"
            )
        
        # Submit button
        submitted = st.form_submit_button(
            "📥 Download Playlist",
            type="primary",
            use_container_width=True
        )
    
    additional_options = {
        'start_index': start_index,
        'end_index': end_index,
        'reverse_order': reverse_order,
        'skip_unavailable': skip_unavailable,
        'max_videos': max_videos
    }
    
    return playlist_url, submitted, additional_options

def show_url_examples():
    """Display examples of valid URLs."""
    
    with st.expander("💡 URL Examples"):
        st.markdown("""
        **Valid YouTube URLs:**
        
        📹 **Regular Videos:**
        - `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
        - `https://youtu.be/dQw4w9WgXcQ`
        
        🎬 **YouTube Shorts:**
        - `https://www.youtube.com/shorts/dQw4w9WgXcQ`
        
        📋 **Playlists:**
        - `https://www.youtube.com/playlist?list=PLrAXtmRdnEQy...`
        - `https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmRdnEQy...`
        """)

def validate_and_clean_url(url: str) -> Tuple[str, bool, str]:
    """
    Validate and clean URL.
    
    Returns:
        Tuple of (cleaned_url, is_valid, error_message)
    """
    if not url:
        return "", False, "Please enter a URL"
    
    url = url.strip()
    
    # Check if it's a valid YouTube URL
    if URLValidator.is_valid_youtube_url(url) or URLValidator.is_valid_youtube_playlist_url(url):
        normalized_url = URLValidator.normalize_url(url)
        return normalized_url, True, ""
    
    # Try to extract URL from text (in case user pasted more than just URL)
    url_pattern = r'https?://(?:www\.)?(?:youtube\.com|youtu\.be)/[^\s]+'
    match = re.search(url_pattern, url)
    
    if match:
        extracted_url = match.group()
        if URLValidator.is_valid_youtube_url(extracted_url) or URLValidator.is_valid_youtube_playlist_url(extracted_url):
            return URLValidator.normalize_url(extracted_url), True, ""
    
    return url, False, "Invalid YouTube URL format"
