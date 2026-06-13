import os
import uuid
import subprocess


def get_instagram_info(url):

    return {
        "title": "Instagram",
        "thumbnail": None,
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

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise Exception(result.stderr)

    allowed_ext = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".mp4",
        ".mov",
        ".mkv",
    }

    downloaded_files = []

    for root, _, files in os.walk(folder):

        for file in files:

            full_path = os.path.join(root, file)

            ext = os.path.splitext(full_path)[1].lower()

            if (
                os.path.isfile(full_path)
                and ext in allowed_ext
            ):
                downloaded_files.append(full_path)

    downloaded_files.sort()

    return downloaded_files
