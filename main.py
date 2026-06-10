import asyncio
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

from config import BOT_TOKEN, ADMIN_ID
from keyboards.reply import main_menu, back_menu
from utils.force_join import is_joined
from keyboards.inline import (
    join_channel_keyboard,
    shorts_keyboard,
    youtube_keyboard,
    instagram_keyboard,
    tiktok_keyboard,
    soundcloud_keyboard,
)
from services.link_detector import detect_platform
from services.youtube import (
    get_video_info,
    is_shorts,
    download_mp3,
    download_video
)
from database.db import (
    create_tables,
    save_url,
    get_url,
    save_user,
    users_count,
    get_all_users,
    users_today
)
from utils.download_lock import active_download
from services.instagram import get_instagram_info, download_instagram
from services.tiktok import (
    get_tiktok_info,
    download_tiktok
)
from services.soundcloud import (
    get_soundcloud_info,
    download_soundcloud
)


broadcast_mode = set()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user = update.effective_user

    save_user(
    user.id,
    user.username,
    user.first_name
  )
    
    user_id = update.effective_user.id

    joined = await is_joined(
        context.bot,
        user_id
    )

    if not joined:
        await update.message.reply_text(
            "برای استفاده از ربات ابتدا عضو کانال شوید!\nو سپس دوباره /start را بزنید!",
            reply_markup=join_channel_keyboard()
        )
        return
    await update.message.reply_text("به ربات دانلودر خوش آمدید!", reply_markup=main_menu())


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
     
     if update.effective_user.id in broadcast_mode:

        users = get_all_users()

        sent = 0

        for user in users:

            try:

                await context.bot.send_message(
                    chat_id=user[0],
                    text=update.message.text
                )

                sent += 1

            except:
                pass

        broadcast_mode.remove(
            update.effective_user.id
        )

        await update.message.reply_text(
            f"ارسال شد به {sent} نفر."
        )

        return

     
     user_id = update.effective_user.id
     joined = await is_joined(
        context.bot,
        user_id
    )
     
     if not joined:
        await update.message.reply_text(
            "برای استفاده از ربات ابتدا عضو کانال شوید!\nو سپس دوباره /start را بزنید!",
            reply_markup=join_channel_keyboard()
        )
        return
     
     text = update.message.text

     if text == "📥 دانلود":
        await update.message.reply_text(
            "لینک خود را ارسال کنید:\n\n(به‌علت سرعت اینترنت ممکن است حین دانلود ارور دریافت کنید اما احتمالاً فایل ارسال خواهد شد. اگر ارسال نشد دوباره تلاش کنید.)",
            reply_markup=back_menu()
        )

     elif text == "❤️ حمایت":
         await update.message.reply_text(
             "💖 حمایت از ما\n\nاگر این ربات برات مفید بود، اون رو به دوستانت معرفی کن.\n\nممنون از حمایتت 🌹",
             reply_markup=back_menu()
         )

     elif text == "🛠️ پشتیبانی":
         await update.message.reply_text(
             "📞 پشتیبانی\n\nاگر نیاز به کمک داری، می‌تونی از طریق این آیدی ما تماس بگیری.\n\nما همیشه برای کمک به تو آماده‌ایم! 🙌\n@MZTDL_Support",
             reply_markup=back_menu()
         )

     elif text == "📖 راهنما":
         await update.message.reply_text(
             """
             برای دانلود در بات:\n\n
۱. دانلود را بزن!\n
۲. لینک پلتفرم مورد نظرت رو ارسال کن!\n
۳. فایل رو دریافت کن!\n\n
برای دانلود در گروه:\n\n
۱. بات رو در گروه به‌عنوان ادمین اضافه کن!\n
۲. لینک پلتفرم مورد نظرت رو توی گروه بفرست!\n
۳. فایل رو دریافت کن!
             """,
             reply_markup=back_menu()
         )

     elif text == "👥 افزودن به گروه (درحال توسعه)":
         await update.message.reply_text(
             "این بخش در حال توسعه است...",
             reply_markup=back_menu()
         )
     
     elif text == "🏠 بازگشت به خانه":
         await update.message.reply_text(
             "منوی اصلی",
             reply_markup=main_menu()
         )


async def handle_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user_id = update.effective_user.id

    joined = await is_joined(
        context.bot,
        user_id
    )
    if not joined:
        await update.message.reply_text(
           "برای استفاده از ربات ابتدا عضو کانال شوید!\nو سپس دوباره /start را بزنید!",
           reply_markup=join_channel_keyboard() 
        )
        return
    text = update.message.text

    if not text.startswith("http"):
        return
    platform = detect_platform(text)

    if platform == "youtube":

        save_url(
            update.effective_user.id,
            text
        )
        
        try:

            info = get_video_info(text)

            if is_shorts(text):

                await update.message.reply_photo(
                    photo=info["thumbnail"],
                    caption=info["title"],
                    reply_markup=shorts_keyboard()
                )

            else:

                await update.message.reply_photo(
                    photo=info["thumbnail"],
                    caption=info["title"],
                    reply_markup=youtube_keyboard()
                )

        except Exception:

            await update.message.reply_text(
                "❌ دانلود این محتوا امکان‌پذیر نیست."
            )


    elif platform == "instagram":

        save_url(
        update.effective_user.id,
        text
     )

        info = get_instagram_info(
        text
     )

        await update.message.reply_photo(
            photo=info["thumbnail"],
            caption=info["title"],
            reply_markup=
            instagram_keyboard()
     )

    elif platform == "tiktok":

        save_url(
        update.effective_user.id,
        text
        )

        info = get_tiktok_info(
            text
        )

        await update.message.reply_photo(
            photo=info["thumbnail"],
            caption=info["title"],
            reply_markup=tiktok_keyboard()
        )

    elif platform == "soundcloud":

        save_url(
            update.effective_user.id,
            text
        )

        info = get_soundcloud_info(
            text
        )

        await update.message.reply_photo(
            photo=info["thumbnail"],
            caption=info["title"],
            reply_markup=
            soundcloud_keyboard()
        )

    elif platform == "spotify":

        await update.message.reply_text("🚧 دانلود از Spotify در حال توسعه است.")


async def callbacks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    if user_id in active_download:

        await query.message.reply_text(
            "⏳ دانلود قبلی شما هنوز تمام نشده است."
        )
        return

    data = query.data

    if data == "youtube_mp3":

        url = get_url(user_id)

        if detect_platform(url) != "youtube":

            await query.message.reply_text(
                "❌ این دکمه منقضی شده است."
            )
            return

        if not url:

            await query.message.reply_text(
                "لینکی پیدا نشد."
            )
            return
        active_download.add(user_id)
        msg = await query.message.reply_text(
            "⏳ در حال دانلود..."
        )

        try:

            file_path = download_mp3(
                url,
                user_id
            )

            with open(file_path, "rb") as audio:

                await query.message.reply_audio(
                    audio=audio
                )
            os.remove(file_path)

            await msg.delete()

        except Exception:

            os.remove(file_path)
            await query.message.reply_text(
                "❌ دانلود ناموفق بود.\n\n(این خطا ممکن است به‌دلیل سرعت اینترنت باشد، چند دقیقه صبر کنید اگر فایل ارسال نشد مجدد تلاش کنید.)"
            )

        finally:

            active_download.discard(user_id)

    if data.startswith("shorts_"):

        url = get_url(user_id)

        if detect_platform(url) != "youtube":

            await query.message.reply_text(
                "❌ این دکمه منقضی شده است."
            )
            return

        if not url:
            await query.message.reply_text(
                "لینکی پیدا نشد."
            )
            return
        active_download.add(user_id)
        quality = data.split("_")[1]

        if quality == "mp3":

            msg = await query.message.reply_text(
                "⏳ در حال دانلود MP3..."
            )

            try:

                file_path = download_mp3(
                    url,
                    user_id
                )

                with open(file_path, "rb") as audio:

                    await query.message.reply_audio(
                        audio=audio
                    )
                os.remove(file_path)

                await msg.delete()

            except Exception:

                os.remove(file_path)
                await query.message.reply_text(
                    "❌ دانلود ناموفق بود.\n\n(این خطا ممکن است به‌دلیل سرعت اینترنت باشد، چند دقیقه صبر کنید اگر فایل ارسال نشد مجدد تلاش کنید.)"
                )

            finally:
                active_download.discard(user_id)

        else:

            msg = await query.message.reply_text(
                f"⏳ دانلود {quality}p..."
            )

            try:

                file_path = download_video(
                    url,
                    user_id,
                    quality
                )

                with open(file_path, "rb") as video:

                    await query.message.reply_video(
                        video=video
                    )
                os.remove(file_path)
             
                await msg.delete()

            except Exception:

                os.remove(file_path)
                await query.message.reply_text(
                    "❌ دانلود ناموفق بود.\n\n(این خطا ممکن است به‌دلیل سرعت اینترنت باشد، چند دقیقه صبر کنید اگر فایل ارسال نشد مجدد تلاش کنید.)"
                )

            finally:
                active_download.discard(user_id)
    
    if data == "instagram_download":

        url = get_url(user_id)

        if detect_platform(url) != "instagram":

            await query.message.reply_text(
                "❌ این دکمه مربوط به آخرین لینک اینستاگرام شما نیست."
            )
            return

        msg = await query.message.reply_text(
            "⏳ در حال دانلود..."
        )

        try:

            file_path = await asyncio.to_thread(
                download_instagram,
                url,
                user_id
            )

            with open(
                file_path,
                "rb"
            ) as video:

                await query.message.reply_video(
                    video=video
                )

            os.remove(file_path)

            await msg.delete()

        except Exception:

            os.remove(file_path)
            await query.message.reply_text(
                "❌ دانلود ناموفق بود.\n\n(این خطا ممکن است به‌دلیل سرعت اینترنت باشد، چند دقیقه صبر کنید اگر فایل ارسال نشد مجدد تلاش کنید.)"
            )


    if data == "tiktok_download":

        url = get_url(user_id)

        msg = await query.message.reply_text(
            "⏳ در حال دانلود..."
        )

        try:

            file_path = await asyncio.to_thread(
                download_tiktok,
                url,
                user_id
            )

            with open(
                file_path,
                "rb"
            ) as video:

                await query.message.reply_video(
                    video=video
                )

            os.remove(file_path)

            await msg.delete()

        except Exception:

            os.remove(file_path)
            await query.message.reply_text(
                "❌ دانلود ناموفق بود.\n\n(این خطا ممکن است به‌دلیل سرعت اینترنت باشد، چند دقیقه صبر کنید اگر فایل ارسال نشد مجدد تلاش کنید.)"
            )


    if data == "soundcloud_mp3":

        url = get_url(user_id)

        msg = await query.message.reply_text(
            "⏳ در حال دانلود..."
        )

        try:

            file_path = await asyncio.to_thread(
                download_soundcloud,
                url,
                user_id
            )

            with open(
                file_path,
                "rb"
            ) as audio:

                await query.message.reply_audio(
                    audio=audio
                )

            os.remove(file_path)

            await msg.delete()

        except Exception:
            
            os.remove(file_path)
            await query.message.reply_text(
                "❌ دانلود ناموفق بود.\n\n(این خطا ممکن است به‌دلیل سرعت اینترنت باشد، چند دقیقه صبر کنید اگر فایل ارسال نشد مجدد تلاش کنید.)"
            )


async def admin_pannel(update: Update, context):
    
    if update.effective_user.id != ADMIN_ID:
        return
    text = (
    "🔧 پنل مدیریت\n\n"
    f"👥 کل کاربران: {users_count()}\n"
    f"🆕 کاربران امروز: {users_today()}"
)

    await update.message.reply_text(text)

async def broadcast(update: Update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    broadcast_mode.add(
        update.effective_user.id
    )

    await update.message.reply_text(
        "پیام همگانی را ارسال کن:"
    )



def main():
    create_tables()
    
    app = Application.builder().token(BOT_TOKEN).connect_timeout(10000).read_timeout(10000).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler( filters.TEXT & ~filters.COMMAND, buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,handle_links),group=1)
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(CommandHandler("admin", admin_pannel))
    app.add_handler(CommandHandler("broadcast", broadcast))
    
    print("Bot Started...")
    
    app.run_polling()


if __name__ == "__main__":
    main()
