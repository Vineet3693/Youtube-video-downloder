
import streamlit as st
import tempfile
import os
import zipfile
import io
import time
from pathlib import Path

# Import our modules with error handling
try:
    from src.downloader.youtube_dl import EnhancedYouTubeDownloader
    from src.utils.validators import URLValidator
except ImportError:
    st.error("Module import error. Please check the file structure.")
    st.stop()

def main():
    st.set_page_config(
        page_title="YouTube Downloader",
        page_icon="🎥",
        layout="wide"
    )
    
    st.title("🎥 YouTube Video Downloader")
    
    # Initialize session state
    if 'download_count' not in st.session_state:
        st.session_state.download_count = 0
    
    # Sidebar settings
    with st.sidebar:
        st.header("⚙️ Settings")
        quality = st.selectbox("Quality", ["720p", "480p", "360p", "best"], index=0)
        format_type = st.selectbox("Format", ["mp4", "webm", "mp3 (audio only)"], index=0)
        
        st.info("💡 Use 720p MP4 for best compatibility")
    
    # Main tabs
    tab1, tab2 = st.tabs(["🎬 Single Video", "📋 Playlist"])
    
    with tab1:
        single_video_tab(quality, format_type)
    
    with tab2:
        playlist_tab(quality, format_type)

def single_video_tab(quality, format_type):
    st.subheader("Download Single Video")
    
    url = st.text_input("YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button("Download Video", type="primary"):
        if url:
            if is_valid_youtube_url(url):
                download_video(url, quality, format_type)
            else:
                st.error("Invalid YouTube URL")
        else:
            st.warning("Please enter a URL")

def playlist_tab(quality, format_type):
    st.subheader("Download Playlist")
    
    playlist_url = st.text_input("Playlist URL:", placeholder="https://www.youtube.com/playlist?list=...")
    max_videos = st.slider("Max videos to download", 1, 20, 5)
    
    if st.button("Download Playlist", type="primary"):
        if playlist_url:
            if is_valid_playlist_url(playlist_url):
                download_playlist(playlist_url, quality, format_type, max_videos)
            else:
                st.error("Invalid playlist URL")
        else:
            st.warning("Please enter a playlist URL")

def is_valid_youtube_url(url):
    """Simple URL validation"""
    return "youtube.com/watch" in url or "youtu.be/" in url

def is_valid_playlist_url(url):
    """Simple playlist URL validation"""
    return "youtube.com/playlist" in url or "list=" in url

def download_video(url, quality, format_type):
    progress_bar = st.progress(0)
    status = st.empty()
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            status.text("🔄 Initializing download...")
            progress_bar.progress(25)
            
            downloader = create_downloader(temp_dir, quality, format_type)
            
            status.text("⬇️ Downloading video...")
            progress_bar.progress(75)
            
            result = downloader.download_video(url)
            
            if result['success']:
                status.text("✅ Download completed!")
                progress_bar.progress(100)
                
                # Offer file for download
                file_path = result['file_path']
                filename = result['filename']
                
                with open(file_path, "rb") as file:
                    st.download_button(
                        label=f"⬇️ Download {filename}",
                        data=file.read(),
                        file_name=filename,
                        mime=get_mime_type(format_type)
                    )
                
                st.session_state.download_count += 1
                st.success(f"Total downloads: {st.session_state.download_count}")
                
            else:
                st.error(f"Download failed: {result['error']}")
                show_error_help(result['error'])
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

def download_playlist(playlist_url, quality, format_type, max_videos):
    progress_bar = st.progress(0)
    status = st.empty()
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            status.text("📋 Fetching playlist...")
            progress_bar.progress(10)
            
            downloader = create_downloader(temp_dir, quality, format_type)
            playlist_info = downloader.get_playlist_info(playlist_url)
            
            if not playlist_info['success']:
                st.error(f"Failed to fetch playlist: {playlist_info['error']}")
                return
            
            videos = playlist_info['videos'][:max_videos]
            total = len(videos)
            
            status.text(f"Found {total} videos to download")
            progress_bar.progress(20)
            
            successful_downloads = []
            
            for i, video in enumerate(videos):
                progress = 20 + (i / total) * 70
                progress_bar.progress(int(progress))
                status.text(f"Downloading {i+1}/{total}: {video['title'][:40]}...")
                
                try:
                    result = downloader.download_video(video['url'])
                    if result['success']:
                        successful_downloads.append(result)
                    time.sleep(1)  # Small delay between downloads
                except:
                    continue
            
            if successful_downloads:
                status.text("📦 Creating ZIP file...")
                progress_bar.progress(95)
                
                zip_buffer = create_zip_file(successful_downloads, playlist_info['title'])
                
                progress_bar.progress(100)
                status.text("✅ Playlist download completed!")
                
                st.download_button(
                    label=f"⬇️ Download ZIP ({len(successful_downloads)} videos)",
                    data=zip_buffer.getvalue(),
                    file_name=f"{playlist_info['title']}.zip",
                    mime="application/zip"
                )
                
                st.success(f"Successfully downloaded {len(successful_downloads)} out of {total} videos")
            else:
                st.error("No videos were successfully downloaded")
                
    except Exception as e:
        st.error(f"Playlist download failed: {str(e)}")

def create_downloader(temp_dir, quality, format_type):
    """Create downloader instance"""
    try:
        return EnhancedYouTubeDownloader(temp_dir, quality, format_type)
    except:
        # Fallback to basic downloader if enhanced version fails
        return BasicYouTubeDownloader(temp_dir, quality, format_type)

def create_zip_file(downloads, playlist_name):
    """Create ZIP file from downloads"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, download in enumerate(downloads):
            file_path = download['file_path']
            filename = download['filename']
            zip_filename = f"{i+1:02d}_{filename}"
            zip_file.write(file_path, zip_filename)
    
    zip_buffer.seek(0)
    return zip_buffer

def show_error_help(error):
    """Show helpful error messages"""
    if "403" in error:
        st.warning("Try lowering the quality (480p or 360p) or switching to audio-only mode.")
    elif "404" in error:
        st.warning("Video not found. It may have been deleted or made private.")
    else:
        st.info("Try a different quality setting or check if the video is accessible.")

def get_mime_type(format_type):
    """Get MIME type for downloads"""
    types = {
        'mp4': 'video/mp4',
        'webm': 'video/webm',
        'mp3 (audio only)': 'audio/mpeg'
    }
    return types.get(format_type, 'application/octet-stream')

# Basic fallback downloader
class BasicYouTubeDownloader:
    def __init__(self, output_dir, quality, format_type):
        self.output_dir = Path(output_dir)
        self.quality = quality
        self.format_type = format_type
        
    def download_video(self, url):
        try:
            import yt_dlp
            
            opts = {
                'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
                'format': 'best[height<=720]' if self.quality != 'best' else 'best',
                'noplaylist': True,
            }
            
            if self.format_type == "mp3 (audio only)":
                opts['format'] = 'bestaudio'
                opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = yt_dlp.extract_info(url, download=False)
                ydl.download([url])
                
                # Find downloaded file
                for file in self.output_dir.iterdir():
                    if file.is_file():
                        return {
                            'success': True,
                            'file_path': str(file),
                            'filename': file.name,
                            'title': info.get('title', 'Unknown')
                        }
            
            return {'success': False, 'error': 'File not found after download'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_playlist_info(self, url):
        try:
            import yt_dlp
            
            opts = {'extract_flat': True, 'quiet': True}
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                videos = []
                for entry in info.get('entries', []):
                    if entry:
                        videos.append({
                            'title': entry.get('title', 'Unknown'),
                            'url': f"https://www.youtube.com/watch?v={entry['id']}"
                        })
                
                return {
                    'success': True,
                    'title': info.get('title', 'Unknown Playlist'),
                    'videos': videos
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    main()
