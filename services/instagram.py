import os
import uuid
import subprocess

from yt_dlp import YoutubeDL


def get_instagram_info(url):

    ydl_opts = {
        "quiet": True,
        "cookiefile": "cookiesins.txt",
    }

    with YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(url, download=False)

        return {
            "title": info.get("title", "Instagram"),
            "thumbnail": info.get("thumbnail"),
        }


def download_instagram(url, user_id):

    os.makedirs("downloads", exist_ok=True)

    unique_id = str(uuid.uuid4())

    folder = os.path.join(
        "downloads",
        f"{user_id}_{unique_id}"
    )

    os.makedirs(folder, exist_ok=True)

    command = [
        "gallery-dl",
        "--cookies",
        "cookiesins.txt",
        "-D",
        folder,
        url,
    ]

    subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )

    downloaded_files = []

    for root, _, files in os.walk(folder):

        for file in files:

            full_path = os.path.join(root, file)

            if os.path.isfile(full_path):

                downloaded_files.append(full_path)

    downloaded_files.sort()

    return downloaded_files
