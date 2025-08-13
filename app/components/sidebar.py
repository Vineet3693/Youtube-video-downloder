
import streamlit as st
from typing import Dict, Any

def render_sidebar() -> Dict[str, Any]:
    """Render sidebar with download settings and return configuration."""
    
    with st.sidebar:
        st.header("⚙️ Download Settings")
        
        # Quality Settings
        st.subheader("🎬 Video Quality")
        quality = st.selectbox(
            "Select Quality",
            options=["best", "1080p", "720p", "480p", "360p", "worst"],
            index=2,  # Default to 720p
            help="Choose video quality. 'best' selects highest available quality."
        )
        
        # Format Settings
        st.subheader("📁 Format Options")
        format_type = st.radio(
            "Download Format",
            options=["mp4", "webm", "mp3 (audio only)"],
            index=0,
            help="Select output format. MP3 extracts audio only."
        )
        
        # Advanced Settings
        with st.expander("🔧 Advanced Settings"):
            max_downloads = st.slider(
                "Max Concurrent Downloads",
                min_value=1,
                max_value=5,
                value=2,
                help="Number of simultaneous downloads (playlist only)"
            )
            
            include_subtitles = st.checkbox(
                "Include Subtitles",
                value=False,
                help="Download available subtitles"
            )
            
            audio_quality = st.selectbox(
                "Audio Quality (MP3)",
                options=["128", "192", "256", "320"],
                index=1,
                help="Audio bitrate in kbps (for MP3 format)"
            )
        
        # Information Section
        st.markdown("---")
        st.subheader("📚 Supported Platforms")
        st.markdown("""
        ✅ YouTube Videos  
        ✅ YouTube Shorts  
        ✅ YouTube Playlists  
        ✅ YouTube Music  
        """)
        
        st.subheader("ℹ️ Tips")
        st.info("""
        💡 **Pro Tips:**
        - Use 720p for best quality/size ratio
        - MP3 format extracts audio only
        - Playlists are downloaded as ZIP files
        - Private/restricted videos may fail
        """)
        
        # Usage Statistics
        if st.session_state.get('download_count', 0) > 0:
            st.subheader("📊 Session Stats")
            st.metric("Downloads", st.session_state.get('download_count', 0))
            st.metric("Success Rate", f"{st.session_state.get('success_rate', 100):.1f}%")
    
    return {
        'quality': quality,
        'format_type': format_type,
        'max_downloads': max_downloads,
        'include_subtitles': include_subtitles,
        'audio_quality': audio_quality
    }
