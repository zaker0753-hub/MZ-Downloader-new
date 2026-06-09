from yt_dlp import YoutubeDL
import os
import uuid



def get_soundcloud_info(url):

    ydl_opts = {
        "quiet": True
    }

    with YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            url,
            download=False
        )

    return {
        "title": info.get("title"),
        "thumbnail": info.get("thumbnail")
    }


def download_soundcloud(
    url,
    user_id
):

    os.makedirs(
        "downloads",
        exist_ok=True
    )

    unique_id = str(
        uuid.uuid4()
    )

    output = (
        f"downloads/{user_id}_{unique_id}"
    )

    ydl_opts = {
        "outtmpl": output,
        "quiet": True,
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }
        ]
    }

    with YoutubeDL(
        ydl_opts
    ) as ydl:

        ydl.download([url])

    return f"{output}.mp3"