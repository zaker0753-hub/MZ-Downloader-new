def detect_platform(url: str):
    
    url = url.lower()

    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"

    elif "instagram.com" in url:
        return "instagram"

    elif "tiktok.com" in url:
        return "tiktok"

    elif "soundcloud.com" in url:
        return "soundcloud"

    elif "spotify.com" in url:
        return "spotify"

    return None