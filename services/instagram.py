import os
import uuid

from yt_dlp import YoutubeDL


def get_instagram_info(url):

    ydl_opts = {"quiet": True}

    with YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            url,
            download=False,
        )

        return {
            "title": info.get("title", "Instagram"),
            "thumbnail": info.get("thumbnail"),
        }


def download_instagram(url, user_id):

    os.makedirs("downloads", exist_ok=True)

    unique_id = str(uuid.uuid4())

    output = f"downloads/{user_id}_{unique_id}.%(ext)s"

    ydl_opts = {
        "outtmpl": output,
        "quiet": True,
    }

    with YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(url, download=True)

        download_files = []

        if info.get("entries"):

            for entry in info["entries"]:
                download_files.append(ydl.prepare_filename(entry))

        else:

            download_files.append(ydl.prepare_filename(info))

    return download_files
