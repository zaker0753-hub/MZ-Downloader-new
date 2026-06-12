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

    before = set(os.listdir("downloads"))

    ydl_opts = {
        "outtmpl": output,
        "quiet": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)

    after = set(os.listdir("downloads"))

    new_files = after - before

    print("NEW FILES:", new_files)
    print("ALL FILES:", after)
    
    return [os.path.join("downloads", file) for file in new_files]
