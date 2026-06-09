from yt_dlp import YoutubeDL
import os
import uuid


def get_video_info(url):

    ydl_opts = {
        "quiet": True,
        "noplaylist": True,
        "cookiefile": "cookies.txt"
    }

    with YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            url,
            download=False
        )

    return {
        "title": info.get("title"),
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration"),
        "id": info.get("id")
    }

def is_shorts(url: str):

    return "/shorts/" in url


def download_mp3(url, user_id):

    os.makedirs("downloads", exist_ok=True)

    unique_id = str(uuid.uuid4())

    output_path = (
        f"downloads/{user_id}_{unique_id}"
    )

    ydl_opts = {
        "cookiefile": "cookies.txt",
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "quiet": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return f"{output_path}.mp3"


def download_video(url, user_id, quality):

    os.makedirs("downloads", exist_ok=True)

    unique_id = str(uuid.uuid4())

    output_template = (
        f"downloads/{user_id}_{unique_id}.%(ext)s"
    )

    ydl_opts = {
        "cookiefile": "cookies.txt",
        "outtmpl": output_template,
        "quiet": True,
        "merge_output_format": "mp4"
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

