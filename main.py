from pathlib import Path
import platform
import subprocess
import toml
from rich.console import Console
from rich.theme import Theme
from pytube import YouTube, Playlist
from download_ffmpeg import download_ffmpeg, show_linux_instructions, show_macos_instructions

# Configuration
SYSTEM = platform.system().lower()
CONFIG_FILE = "config.toml"
config = toml.load(CONFIG_FILE)

# FFmpeg path detection
FFMPEG_DIR = Path(config["ffmpeg"]["directory"])
if SYSTEM == "windows":
    FFMPEG_EXE = FFMPEG_DIR / "ffmpeg.exe"
    download_ffmpeg()
else:
    FFMPEG_EXE = "ffmpeg"
    show_linux_instructions()
    show_macos_instructions()

# Load configuration from TOML file
CONFIG_FILE = "config.toml"
config = toml.load(CONFIG_FILE)

# Get configurations
FFMPEG_URL = config["ffmpeg"]["url"]
FFMPEG_ARCHIVE = config["ffmpeg"]["archive_name"]
FFMPEG_DIR = Path(config["ffmpeg"]["directory"])
FFMPEG_EXE = FFMPEG_DIR / config["ffmpeg"]["executable"]

VIDEO_URLS = config["youtube"]["video_urls"]
PLAYLIST_URL = config["youtube-playlist"]["playlist_url"]
OUTPUT_DIR = Path(config["output"]["directory"])

# Define a custom theme with the necessary styles
custom_theme = Theme({
    "info": "cyan",
    "success": "green",
    "danger": "red bold"
})

# Initialize the console with the custom theme
console = Console(theme=custom_theme)

def check_ffmpeg():
    """Checks the availability of FFmpeg"""
    if SYSTEM == "windows":
        return FFMPEG_EXE.exists()
    else:
        try:
            subprocess.run([FFMPEG_EXE, "-version"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

def convert_mp4_to_mp3(mp4_path: Path, mp3_path: Path):
    """Conversion with OS adaptation"""
    try:
        console.print(f"Converting {mp4_path}...", style="info")
        subprocess.run([
            FFMPEG_EXE,
            "-i", str(mp4_path),
            "-vn",  # Disable video
            "-acodec", "libmp3lame",  # MP3 Codec
            "-q:a", "2",  # Quality (0=best, 9=worst)
            str(mp3_path)
        ], check=True)
        
        mp4_path.unlink()
        console.print(f"✅ {mp4_path} converted and deleted", style="success")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Conversion error: {e}", style="danger")
        raise

def download_video(url: str, output_dir: Path) -> Path:
    """Downloads a YouTube video and returns the MP4 file path."""
    try:
        console.print(f"Downloading video from {url}...", style="info")
        yt = YouTube(url)
        video_stream = yt.streams.filter(file_extension="mp4").first()
        if not video_stream:
            raise ValueError("No MP4 stream available for this video.")
        downloaded_file = video_stream.download(output_path=str(output_dir))
        return Path(downloaded_file)
    except Exception as e:
        console.print(f"Error during download: {e}", style="danger")
        raise

def is_valid_youtube_url(url: str) -> bool:
    """
    Checks if a URL is a valid YouTube URL.
    Uses pytube to test if the video actually exists.
    """
    try:
        YouTube(url)  # Attempt to load the video
        return True
    except Exception:
        return False

def process_playlist(playlist_url: str, output_dir: Path):
    """Processes a YouTube playlist (download and conversion)."""
    try:
        console.print(f"Processing playlist: {playlist_url}...", style="info")
        playlist = Playlist(playlist_url)
        for video in playlist.videos:
            url = video.watch_url
            if not is_valid_youtube_url(url):
                console.print(f"Invalid URL ignored: {url}", style="danger")
                continue

            try:
                # Download the video
                mp4_file = download_video(url, output_dir)

                # Define the MP3 file path
                mp3_file = output_dir / f"{mp4_file.stem}.mp3"

                # Convert to MP3
                convert_mp4_to_mp3(mp4_file, mp3_file)

                console.print(f"Processing completed for {url}", style="success")
            except Exception as e:
                console.print(f"Processing failed for {url}: {e}", style="danger")
    except Exception as e:
        console.print(f"Error during playlist processing: {e}", style="danger")

def process_videos(video_urls: list, output_dir: Path):
    """Processes a list of videos (download and conversion)."""
    for url in video_urls:
        if not is_valid_youtube_url(url):
            console.print(f"Invalid URL ignored: {url}", style="danger")
            continue

        try:
            # Download the video
            mp4_file = download_video(url, output_dir)

            # Define the MP3 file path
            mp3_file = output_dir / f"{mp4_file.stem}.mp3"

            # Convert to MP3
            convert_mp4_to_mp3(mp4_file, mp3_file)

            console.print(f"Processing completed for {url}", style="success")
        except Exception as e:
            console.print(f"Processing failed for {url}: {e}", style="danger")

def main():
    try:
        # Create output directory if it doesn't exist
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Process individual videos
        if VIDEO_URLS:
            process_videos(VIDEO_URLS, OUTPUT_DIR)

        # Process playlist
        if PLAYLIST_URL:
            process_playlist(PLAYLIST_URL, OUTPUT_DIR)

        console.print("All videos processing completed!", style="success")
    except Exception as e:
        console.print(f"A critical error occurred: {e}", style="danger")
        exit(1)

if __name__ == "__main__":
    main()