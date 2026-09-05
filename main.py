import argparse
import os
from pathlib import Path
import platform
import shutil
import sys

# Force UTF-8 on Windows consoles to prevent cp1252 charmap encoding errors
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import toml
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
import yt_dlp
from download_ffmpeg import download_ffmpeg, show_linux_instructions, show_macos_instructions

# Theme configuration
custom_theme = Theme({
    "info": "cyan",
    "success": "green bold",
    "warning": "yellow",
    "danger": "red bold"
})
console = Console(theme=custom_theme, legacy_windows=False)

SYSTEM = platform.system().lower()
DEFAULT_CONFIG = "config.toml"
EXAMPLE_CONFIG = "config.example.toml"


def load_configuration(config_path: str = DEFAULT_CONFIG) -> dict:
    """Loads configuration from TOML file, falling back to example if needed."""
    cfg_file = Path(config_path)
    if not cfg_file.exists():
        example_file = Path(EXAMPLE_CONFIG)
        if example_file.exists():
            console.print(f"[warning]'{config_path}' introuvable. Copie depuis '{EXAMPLE_CONFIG}'...[/]")
            shutil.copy(example_file, cfg_file)
        else:
            console.print(f"[danger]Fichier de configuration '{config_path}' manquant.[/]")
            return {
                "ffmpeg": {"directory": "auto", "executable": "ffmpeg.exe"},
                "youtube": {"video_urls": [], "cookies_from_browser": "firefox"},
                "youtube-playlist": {"playlist_url": ""},
                "output": {"directory": "mp3", "audio_quality": "0"}
            }

    try:
        return toml.load(cfg_file)
    except Exception as e:
        console.print(f"[danger]Erreur de lecture de '{config_path}': {e}[/]")
        raise


def resolve_ffmpeg(config_ffmpeg_dir: str | None = None) -> str:
    """
    Finds the FFmpeg executable or directory.
    Checks:
    1. Configured directory (if not empty or "auto")
    2. C:\\ffmpeg\\dist\\bin (Windows standard path)
    3. System PATH
    4. Local project ./ffmpeg directory
    5. Fallback download for Windows
    """
    # 1. Configured directory
    if config_ffmpeg_dir and config_ffmpeg_dir.strip() and config_ffmpeg_dir.strip().lower() != "auto":
        p = Path(config_ffmpeg_dir)
        if p.is_file() and p.name.lower().startswith("ffmpeg"):
            return str(p.parent)
        if p.is_dir() and (p / "ffmpeg.exe").exists():
            return str(p)
        if p.is_dir() and (p / "ffmpeg").exists():
            return str(p)

    # 2. Windows C:\ffmpeg\dist\bin
    if SYSTEM == "windows":
        custom_win_path = Path(r"C:\ffmpeg\dist\bin")
        if custom_win_path.is_dir() and (custom_win_path / "ffmpeg.exe").exists():
            return str(custom_win_path)

    # 3. System PATH
    which_ffmpeg = shutil.which("ffmpeg")
    if which_ffmpeg:
        return str(Path(which_ffmpeg).parent)

    # 4. Local ./ffmpeg
    local_ffmpeg = Path("ffmpeg")
    exe_name = "ffmpeg.exe" if SYSTEM == "windows" else "ffmpeg"
    if (local_ffmpeg / exe_name).exists():
        return str(local_ffmpeg)

    # 5. Automatic download on Windows or instructions
    if SYSTEM == "windows":
        console.print("[warning]FFmpeg n'a pas été trouvé. Tentative de téléchargement automatique...[/]")
        if download_ffmpeg(target_dir="ffmpeg"):
            return str(local_ffmpeg)
        raise FileNotFoundError("Impossible de localiser ou installer FFmpeg.")
    elif SYSTEM == "darwin":
        show_macos_instructions()
        raise FileNotFoundError("FFmpeg est requis sur macOS.")
    else:
        show_linux_instructions()
        raise FileNotFoundError("FFmpeg est requis sur Linux.")


def detect_js_runtime() -> dict:
    """Detects available JS runtimes (node, bun, deno) to solve YouTube challenges."""
    runtimes = {}
    for runtime in ["deno", "node", "bun"]:
        which_path = shutil.which(runtime)
        if which_path:
            runtimes[runtime] = {"path": which_path}
    if not runtimes:
        runtimes["node"] = {"path": None}
    return runtimes


def build_ydl_options(
    output_dir: Path,
    ffmpeg_location: str,
    audio_quality: str = "0",
    cookies_browser: str | None = None
) -> dict:
    """Constructs yt-dlp configuration options for MP3 extraction."""
    js_runtimes = detect_js_runtime()
    
    opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": str(audio_quality),
        }],
        "ffmpeg_location": ffmpeg_location,
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "ignoreerrors": True,
        "no_warnings": False,
        "quiet": False,
        "js_runtimes": js_runtimes,
        "remote_components": ["ejs:github"],
    }

    if cookies_browser and cookies_browser.strip():
        browser_name = cookies_browser.strip().lower()
        opts["cookiesfrombrowser"] = (browser_name, None, None, None)

    return opts


def process_urls(urls: list[str], output_dir: Path, ydl_opts: dict):
    """Downloads and converts YouTube videos/playlists using yt-dlp."""
    output_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[info]📂 Dossier de sortie :[/] {output_dir.resolve()}")
    console.print(f"[info]🎞️  Nombre de sources à traiter :[/] {len(urls)}")

    success_count = 0
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for idx, url in enumerate(urls, start=1):
            console.print(f"\n[info]━━━ ({idx}/{len(urls)}) Traitement de : {url} ━━━[/]")
            try:
                ret = ydl.download([url])
                if ret == 0:
                    success_count += 1
                    console.print(f"[success]✅ Terminé avec succès pour {url}[/]")
                else:
                    console.print(f"[danger]❌ Échec pour {url} (code {ret})[/]")
            except Exception as e:
                console.print(f"[danger]❌ Erreur lors du traitement de {url}: {e}[/]")
                if "Sign in to confirm" in str(e):
                    console.print(
                        "[warning]💡 Astuce: YouTube demande une vérification. Vérifiez que 'cookies_from_browser' "
                        "est bien activé dans config.toml (ex: 'firefox', 'chrome' ou 'edge').[/]"
                    )

    console.print(f"\n[success]🎉 Traitement terminé : {success_count}/{len(urls)} réussi(s) ![/]")


def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="YouTubeToMP3 - Téléchargement et conversion de vidéos/playlists YouTube en MP3"
    )
    parser.add_argument("urls", nargs="*", help="URLs de vidéos ou de playlists YouTube à télécharger")
    parser.add_argument("-c", "--config", default=DEFAULT_CONFIG, help=f"Chemin vers le fichier de config (défaut: {DEFAULT_CONFIG})")
    parser.add_argument("-o", "--output", help="Dossier de destination pour les fichiers MP3")
    parser.add_argument("-b", "--browser", help="Navigateur d'où importer les cookies (ex: firefox, chrome, edge)")
    parser.add_argument("-q", "--quality", help="Qualité audio MP3 (0 = meilleure, 9 = plus basse)")
    parser.add_argument("--ffmpeg", help="Chemin vers le dossier ou l'exécutable FFmpeg")
    return parser.parse_args()


def main():
    args = parse_arguments()
    console.print(Panel.fit("[bold cyan]YouTubeToMP3[/] [dim]v1.0 (yt-dlp + FFmpeg + uv)[/dim]", border_style="cyan"))

    # Load configuration file
    config = load_configuration(args.config)

    # Resolve FFmpeg
    ffmpeg_dir_cfg = args.ffmpeg or config.get("ffmpeg", {}).get("directory")
    try:
        ffmpeg_location = resolve_ffmpeg(ffmpeg_dir_cfg)
        console.print(f"[success]🔧 FFmpeg détecté :[/] {ffmpeg_location}")
    except Exception as e:
        console.print(f"[danger]Erreur FFmpeg: {e}[/]")
        sys.exit(1)

    # Determine URLs
    urls_to_process = []
    if args.urls:
        urls_to_process.extend(args.urls)
    else:
        cfg_urls = config.get("youtube", {}).get("video_urls", [])
        if isinstance(cfg_urls, list):
            urls_to_process.extend([u for u in cfg_urls if u and u.strip()])
        elif isinstance(cfg_urls, str) and cfg_urls.strip():
            urls_to_process.append(cfg_urls.strip())

        playlist = config.get("youtube-playlist", {}).get("playlist_url", "")
        if playlist and playlist.strip():
            urls_to_process.append(playlist.strip())

    if not urls_to_process:
        console.print("[warning]Aucune URL spécifiée. Renseignez 'video_urls' dans config.toml ou passez une URL en argument.[/]")
        console.print("[info]Exemple: uv run main.py https://youtu.be/...[/]")
        return

    # Output directory & audio quality
    output_str = args.output or config.get("output", {}).get("directory", "mp3")
    output_dir = Path(output_str)

    quality = args.quality or str(config.get("output", {}).get("audio_quality", "0"))
    cookies_browser = args.browser or config.get("youtube", {}).get("cookies_from_browser", "firefox")

    if cookies_browser:
        console.print(f"[info]🍪 Import des cookies depuis :[/] {cookies_browser}")

    ydl_opts = build_ydl_options(
        output_dir=output_dir,
        ffmpeg_location=ffmpeg_location,
        audio_quality=quality,
        cookies_browser=cookies_browser
    )

    process_urls(urls_to_process, output_dir, ydl_opts)


if __name__ == "__main__":
    main()