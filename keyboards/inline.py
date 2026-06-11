from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import CHANNEL_USERNAME


def join_channel_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "📢 عضویت در کانال",
                url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}",
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def shorts_keyboard():

    keyboard = [
        [InlineKeyboardButton("🎥 360p", callback_data="shorts_360")],
        [InlineKeyboardButton("🎥 480p", callback_data="shorts_480")],
        [InlineKeyboardButton("🎥 720p", callback_data="shorts_720")],
        [InlineKeyboardButton("🎥 1080p", callback_data="shorts_1080")],
        [InlineKeyboardButton("🎵 MP3", callback_data="shorts_mp3")],
    ]

    return InlineKeyboardMarkup(keyboard)


def youtube_keyboard():

    keyboard = [
        [InlineKeyboardButton("🎥 360p(پارت‌پارت)", callback_data="youtube_360")],
        [InlineKeyboardButton("🎥 480p(پارت‌پارت)", callback_data="youtube_480")],
        [InlineKeyboardButton("🎥 720p(پارت‌پارت)", callback_data="youtube_720")],
        [InlineKeyboardButton("🎥 1080p(پارت‌پارت)", callback_data="youtube_1080")],
        [InlineKeyboardButton("🎵 MP3", callback_data="youtube_mp3")],
    ]

    return InlineKeyboardMarkup(keyboard)


def instagram_keyboard():
    keyboard = [[InlineKeyboardButton("📥 دانلود", callback_data="instagram_download")]]

    return InlineKeyboardMarkup(keyboard)


def tiktok_keyboard():

    keyboard = [[InlineKeyboardButton("📥 دانلود", callback_data="tiktok_download")]]

    return InlineKeyboardMarkup(keyboard)


def soundcloud_keyboard():

    keyboard = [[InlineKeyboardButton("🎵 دانلود MP3", callback_data="soundcloud_mp3")]]

    return InlineKeyboardMarkup(keyboard)
