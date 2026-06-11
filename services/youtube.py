import math
import os
import subprocess
import uuid

import json
from mutagen.mp3 import MP3
from yt_dlp import YoutubeDL


def get_video_info(url):

    ydl_opts = {"quiet": True, "noplaylist": True, "cookiefile": "cookies.txt"}

    with YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(url, download=False)

    return {
        "title": info.get("title"),
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration"),
        "id": info.get("id"),
    }


def is_shorts(url: str):

    return "/shorts/" in url


def download_mp3(url, user_id):

    os.makedirs("downloads", exist_ok=True)

    unique_id = str(uuid.uuid4())

    output_path = f"downloads/{user_id}_{unique_id}"

    ydl_opts = {
        "cookiefile": "cookies.txt",
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "quiet": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }
        ],
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return f"{output_path}.mp3"


def get_audio_duration(file_path):

    audio = MP3(file_path)

    return int(audio.info.length)


def split_mp3(file_path, segment_time=1200):

    output_pattern = file_path.replace(".mp3", "_part_%03d.mp3")

    subprocess.run(
        [
            "ffmpeg",
            "-i",
            file_path,
            "-f",
            "segment",
            "-segment_time",
            str(segment_time),
            "-c",
            "copy",
            output_pattern,
        ],
        check=True,
    )

    parts = []

    folder = os.path.dirname(file_path)

    base = os.path.basename(file_path).replace(".mp3", "_part_")

    for file in sorted(os.listdir(folder)):

        if file.startswith(base) and file.endswith(".mp3"):

            parts.append(os.path.join(folder, file))

    return parts


def download_video(url, user_id, quality):

    os.makedirs("downloads", exist_ok=True)

    unique_id = str(uuid.uuid4())

    output_template = f"downloads/{user_id}_{unique_id}.%(ext)s"

    ydl_opts = {
        "cookiefile": "cookies.txt",
        "outtmpl": output_template,
        "quiet": True,
        "merge_output_format": "mp4",
    }

    if quality == "360":
        ydl_opts["format"] = "bestvideo[height<=360]+bestaudio/best"

    elif quality == "480":
        ydl_opts["format"] = "bestvideo[height<=480]+bestaudio/best"

    elif quality == "720":
        ydl_opts["format"] = "bestvideo[height<=720]+bestaudio/best"

    elif quality == "1080":
        ydl_opts["format"] = "bestvideo[height<=1080]+bestaudio/best"

    with YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(url, download=True)

        filename = ydl.prepare_filename(info)

    return os.path.splitext(filename)[0] + ".mp4"


def get_video_duration(file_path):

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            file_path,
        ],
        capture_output=True,
        text=True,
    )

    data = json.loads(result.stdout)

    return float(data["format"]["duration"])


def split_video_by_size(input_file, max_size_mb=30):

    file_size = os.path.getsize(input_file)

    max_size = max_size_mb * 1024 * 1024

    if file_size <= max_size:
        return [input_file]

    duration = get_video_duration(input_file)

    parts_count = math.ceil(file_size / max_size)

    part_duration = math.ceil(duration / parts_count)

    output_files = []

    base_name = os.path.splitext(input_file)[0]

    for i in range(parts_count):

        output_file = f"{base_name}_part{i+1}.mp4"

        start_time = i * part_duration

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                input_file,
                "-ss",
                str(start_time),
                "-t",
                str(part_duration),
                "-c",
                "copy",
                output_file,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        output_files.append(output_file)

    return output_files
