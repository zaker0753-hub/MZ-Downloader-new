import os
import uuid
import instaloader


def get_instagram_info(url):

    return {
        "title": "Instagram Post",
        "thumbnail": None,
    }


def download_instagram(url, user_id):

    os.makedirs("downloads", exist_ok=True)

    shortcode = url.rstrip("/").split("/")[-1]

    L = instaloader.Instaloader(
        download_videos=True,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        dirname_pattern="downloads",
        filename_pattern=f"{user_id}_{uuid.uuid4()}",
    )

    post = instaloader.Post.from_shortcode(
        L.context,
        shortcode,
    )

    before = set(os.listdir("downloads"))

    L.download_post(post, target="")

    after = set(os.listdir("downloads"))

    files = []

    for file in after - before:

        if file.endswith(
            (
                ".jpg",
                ".jpeg",
                ".png",
                ".mp4",
                ".webp",
            )
        ):
            files.append(
                os.path.join(
                    "downloads",
                    file,
                )
            )

    return files
