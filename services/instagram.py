import os
import uuid

from yt_dlp import YoutubeDL


def get_instagram_info(url):

    ydl_opts = {"quiet": True, "cookiefile": "cookiesins.txt"}

    with YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(url, download=False)

        return {
            "title": info.get("title", "Instagram"),
            "thumbnail": info.get("thumbnail"),
        }
    


def download_instagram(url, user_id):

    os.makedirs("downloads", exist_ok=True)

    unique_id = str(uuid.uuid4())

    output = f"downloads/" f"{user_id}_{unique_id}_%(playlist_index)s.%(ext)s"

    ydl_opts = {"outtmpl": output, "quiet": True, "merge_output_format": "mp4", "cookiefile": "cookiesins.txt"}

    downloaded_files = []

    with YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(url, download=True)

        if "entries" in info:

            for entry in info["entries"]:

                try:

                    filename = ydl.prepare_filename(entry)

                    if os.path.exists(filename):

                        downloaded_files.append(filename)

                except Exception:
                    pass

        else:

            filename = ydl.prepare_filename(info)

            if os.path.exists(filename):

                downloaded_files.append(filename)

    return downloaded_files
