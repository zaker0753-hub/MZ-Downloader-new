from telegram.error import TelegramError
from config import  CHANNEL_USERNAME

async def is_joined(bot, user_id):

    try:
        member = await bot.get_chat_member(
            chat_id = CHANNEL_USERNAME,
            user_id=user_id
        )
        return member.status in [
            "member",
            "administrator",
            "creator"
        ]
    except TelegramError:
        return False