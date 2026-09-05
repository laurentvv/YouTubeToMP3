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

def find_7zip():
    """Finds 7-Zip executable."""
    import shutil
    which_7z = shutil.which("7z")
    if which_7z:
        return which_7z
    for path in [
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe",
    ]:
        if os.path.exists(path):
            return path
    return None

def download_ffmpeg(target_dir: str = FFMPEG_DIR):
    """Download and extract the latest version of ffmpeg."""
    target_exe = os.path.join(target_dir, "ffmpeg.exe")
    if not os.path.exists(target_exe):
        seven_zip = find_7zip()
        if not seven_zip:
            console.print("7-Zip introuvable. Veuillez installer 7-Zip ou installer FFmpeg manuellement.", style="danger")
            return False

        console.print("Downloading ffmpeg...", style="info")
        urllib.request.urlretrieve(FFMPEG_URL, FFMPEG_7Z)
        console.print("Download complete. Extracting...", style="info")

        os.makedirs(target_dir, exist_ok=True)
        
        subprocess.run([
            seven_zip,
            "e",
            FFMPEG_7Z,
            "ffmpeg-*-essentials_build/bin/ffmpeg.exe",
            f"-o{target_dir}",
            "-y"
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if not os.path.exists(target_exe):
            console.print(f"Error: {target_exe} was not extracted correctly", style="danger")
            raise FileNotFoundError(f"ffmpeg.exe not found in {target_dir}")
        
        console.print("Extraction complete. ffmpeg.exe available.", style="info")

        if os.path.exists(FFMPEG_7Z):
            os.remove(FFMPEG_7Z)
        return True
    else:
        console.print("ffmpeg is already downloaded.", style="info")
        return True

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