# YouTubeToMP3

[![Python Version](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A Python tool to download YouTube videos and convert them to MP3 files. This script is easy to use, configurable via a `.toml` file, and supports multiple URLs simultaneously.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
   - [Windows](#installation-on-windows)
   - [macOS](#installation-on-macos)
   - [Linux](#installation-on-linux)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Contributions](#contributions)
7. [License](#license)

---

## Overview

**YouTubeToMP3** is a convenient tool for extracting audio from YouTube videos and converting them to MP3 files. It uses popular libraries like `pytube` for downloading and `ffmpeg` for audio conversion. All configurations are centralized in a `.toml` file, allowing for easy customization and simplified management.

---

## Features

- **Multiple Downloads**: Supports multiple YouTube URLs simultaneously.
- **Playlist Support**: Automatically downloads all videos from a YouTube playlist.
- **URL Validation**: Verifies that each URL is valid before processing the video.
- **Automatic Conversion**: Converts downloaded videos to MP3 using FFmpeg.
- **Modular Configuration**: All parameters (paths, URLs, etc.) are defined in a `.toml` file.
- **Clear Messages**: Displays informative messages about operation progress.
- **Temporary File Cleanup**: Automatically removes `.mp4` files after conversion.

---

## Installation

### General Prerequisites

- Python 3.13
- FFmpeg
  - Windows: Automatic installation by the script
  - Linux/macOS: To be installed via system repositories

### Installation on Windows

1. **Install 7-Zip** (necessary to extract FFmpeg):
   For Windows, ffmpeg.exe is already in the ffmpeg directory.
   - Download 7-Zip from [the official website](https://www.7-zip.org/download.html)
   - Run the installation file and follow the instructions
   - Ensure the default location (`C:\Program Files\7-Zip\7z.exe`) is used

2. **Clone the repository**:
   ```bash
   git clone https://github.com/laurentvv/YouTubeToMP3.git
   cd YouTubeToMP3
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**:
   ```bash
   cp config.example.toml config.toml
   ```

5. FFmpeg will be automatically downloaded during the first execution of the script.

### Installation on macOS

1. **Install FFmpeg** using one of these methods:
   - With Homebrew:
     ```bash
     brew install ffmpeg
     ```
   - Direct download from [evermeet.cx/ffmpeg](https://evermeet.cx/ffmpeg/)

2. **Clone the repository**:
   ```bash
   git clone https://github.com/laurentvv/YouTubeToMP3.git
   cd YouTubeToMP3
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**:
   ```bash
   cp config.example.toml config.toml
   ```

### Installation on Linux

1. **Install FFmpeg**:
   ```bash
   # Debian/Ubuntu
   sudo apt install ffmpeg
   
   # Fedora
   sudo dnf install ffmpeg
   
   # Arch Linux
   sudo pacman -S ffmpeg
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/laurentvv/YouTubeToMP3.git
   cd YouTubeToMP3
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**:
   ```bash
   cp config.example.toml config.toml
   ```

---

## Configuration

The `config.toml` file contains all necessary parameters:

### Section `[ffmpeg]`
- `url`: Link to the FFmpeg archive (if you haven't already installed it).
- `archive_name`: Name of the FFmpeg archive file.
- `directory`: Directory where FFmpeg will be extracted.
- `executable`: Name of the FFmpeg executable.

### Section `[youtube]`
- `video_urls`: List of YouTube URLs to download and convert.

### Section `[youtube-playlist]`
- `playlist_url`: URL of the YouTube playlist to download completely.

### Section `[output]`
- `directory`: Directory where MP3 files will be saved.

---

## Usage

### Example Output

```bash
[info] FFmpeg is installed.
[info] Downloading video from https://www.youtube.com/watch?v=zK6NtwHIjjg...
[info] Converting D:\MP3\video1.mp4 to D:\MP3\video1.mp3...
[success] File D:\MP3\video1.mp4 deleted.
[success] Processing completed for https://www.youtube.com/watch?v=zK6NtwHIjjg
[info] Processing playlist: https://www.youtube.com/playlist?list=PLaJwbiPX90jydet2NStKyh8YIc6d8_pgX...
[success] Processing of all videos completed!
```

### Adding New Videos

To add new videos, simply modify the `video_urls` list in the `config.toml` file.

### Downloading a Playlist

Add the playlist URL in the `playlist_url` field of the `config.toml` file.

---

## Contributions

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork this repository.
2. Create a branch for your feature (`git checkout -b feature/feature-name`).
3. Commit your changes (`git commit -m 'Add XYZ feature'`).
4. Push to the branch (`git push origin feature/feature-name`).
5. Open a pull request.

---

## License

This project is under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## Support

If you encounter any problems or have questions, don't hesitate to open an issue in this repository.

---

## Acknowledgments

- Thanks to [`pytube`](https://github.com/pytube/pytube) for their excellent YouTube download module.
- Thanks to [`rich`](https://github.com/Textualize/rich) for colorful console messages.
- Thanks to [`ffmpeg`](https://ffmpeg.org/) for audio conversion.