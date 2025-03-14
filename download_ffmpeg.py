import subprocess
import os
import urllib.request
from rich.console import Console
from rich.theme import Theme

# Configuration
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z"
FFMPEG_7Z = "ffmpeg-git-essentials.7z"
FFMPEG_DIR = r"ffmpeg"
FFMPEG_EXE = os.path.join(FFMPEG_DIR, "ffmpeg.exe")

# Define a custom theme with necessary styles
custom_theme = Theme({
    "info": "cyan",
    "success": "green",
    "danger": "red bold"
})

# Initialize console with the custom theme
console = Console(theme=custom_theme)

def download_ffmpeg():
    """Download and extract the latest version of ffmpeg."""
    if not os.path.exists(FFMPEG_EXE):
        console.print("Downloading ffmpeg...", style="info")
        # Download ffmpeg
        urllib.request.urlretrieve(FFMPEG_URL, FFMPEG_7Z)
        console.print("Download complete. Extracting...", style="info")

        # Create destination folder if needed
        os.makedirs(FFMPEG_DIR, exist_ok=True)
        
        # Extract only ffmpeg.exe with exact path
        subprocess.run([
            r"C:\Program Files\7-Zip\7z.exe",
            "e",
            FFMPEG_7Z,
            "ffmpeg-*-essentials_build/bin/ffmpeg.exe",
            f"-o{FFMPEG_DIR}",
            "-y"
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Verify that ffmpeg.exe was extracted correctly
        if not os.path.exists(FFMPEG_EXE):
            console.print(f"Error: {FFMPEG_EXE} was not extracted correctly", style="danger")
            raise FileNotFoundError(f"ffmpeg.exe not found in {FFMPEG_DIR}")
        
        console.print("Extraction complete. ffmpeg.exe available.", style="info")

        # Clean up the 7z file
        os.remove(FFMPEG_7Z)
    else:
        console.print("ffmpeg is already downloaded.", style="info")

def show_linux_instructions():
    """LINUX instruction ffmpeg."""
    console.print("""
    [bold]For Linux:[/]
    - Debian/Ubuntu: [cyan]sudo apt install ffmpeg[/]
    - Red Hat/CentOS: [cyan]sudo dnf install ffmpeg[/]
    - Arch: [cyan]sudo pacman -S ffmpeg[/]
    """, style="info")

def show_macos_instructions():
    """MACOS instruction ffmpeg."""
    console.print("""
    [bold]For macOS:[/]
    - With Homebrew: [cyan]brew install ffmpeg[/]
    - Direct download: [link=https://evermeet.cx/ffmpeg/]https://evermeet.cx/ffmpeg/[/]
    """, style="info")

if __name__ == "__main__":
    download_ffmpeg()