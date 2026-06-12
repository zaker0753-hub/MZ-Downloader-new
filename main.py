import asyncio
import os
import time

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import ADMIN_ID, BOT_TOKEN
from database.db import (
    create_tables,
    get_all_users,
    get_url,
    save_url,
    save_user,
    users_count,
    users_today,
)
from keyboards.inline import (
    instagram_keyboard,
    join_channel_keyboard,
    shorts_keyboard,
    soundcloud_keyboard,
    tiktok_keyboard,
    youtube_keyboard,
)
from keyboards.reply import back_menu, main_menu
from services.instagram import download_instagram, get_instagram_info
from services.link_detector import detect_platform
from services.soundcloud import download_soundcloud, get_soundcloud_info
from services.tiktok import download_tiktok, get_tiktok_info
from services.youtube import (
    download_mp3,
    download_video,
    get_audio_duration,
    get_video_duration,
    get_video_info,
    is_shorts,
    split_mp3,
    split_video_by_size,
)
from utils.download_lock import active_download
from utils.force_join import is_joined

broadcast_mode = set()
download_semaphore = asyncio.Semaphore(3)
download_queue = asyncio.Queue()
average_download_times = []


def get_average_download_time():

    if not average_download_times:
        return 120

    return int(sum(average_download_times) / len(average_download_times))


def estimate_wait_time(position):
    avg = get_average_download_time()

    batches = (position - 1) // 3

    return batches * avg


async def queue_status_loop(
    user_id,
    status_message,
):

    while True:
        try:
            position = None

            queue_items = list(download_queue._queue)

            for index, item in enumerate(queue_items):
                if item["user_id"] == user_id:
                    position = index + 1
                    break
                if position is None:
                    return
                wait_time = estimate_wait_time(position)

                await status_message.edit_text(
                    f"⏳ در صف دانلود\n\n"
                    f"📍 جایگاه شما: {position}\n"
                    f"🕒 زمان تقریبی انتظار: {wait_time // 60} دقیقه"
                )

                await asyncio.sleep(5)
        except:
            return


async def download_worker(worker_id):
    while True:
        job = await download_queue.get()

        try:
            await job["task"]()

        except Exception as e:
            print(f"Worker {worker_id}: {e}")

        finally:
            download_queue.task_done()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    save_user(user.id, user.username, user.first_name)

    user_id = update.effective_user.id

    joined = await is_joined(context.bot, user_id)

    if not joined:
        await update.message.reply_text(
            "برای استفاده از ربات ابتدا عضو کانال شوید!\nو سپس دوباره /start را بزنید!",
            reply_markup=join_channel_keyboard(),
        )
        return
    await update.message.reply_text(
        "به ربات دانلودر خوش آمدید!", reply_markup=main_menu()
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id in broadcast_mode:

        users = get_all_users()

        sent = 0

        for user in users:

            try:

                await context.bot.send_message(
                    chat_id=user[0], text=update.message.text
                )

                sent += 1

            except:
                pass

        broadcast_mode.remove(update.effective_user.id)

        await update.message.reply_text(f"ارسال شد به {sent} نفر.")

        return

    user_id = update.effective_user.id
    joined = await is_joined(context.bot, user_id)

    if not joined:
        await update.message.reply_text(
            "برای استفاده از ربات ابتدا عضو کانال شوید!\nو سپس دوباره /start را بزنید!",
            reply_markup=join_channel_keyboard(),
        )
        return

    text = update.message.text

    if text == "📥 دانلود":
        await update.message.reply_text(
            "لینک خود را ارسال کنید:\n\n(به‌علت سرعت اینترنت ممکن است حین دانلود ارور دریافت کنید اما احتمالاً فایل ارسال خواهد شد. اگر ارسال نشد دوباره تلاش کنید.)",
            reply_markup=back_menu(),
        )

    elif text == "❤️ حمایت":
        await update.message.reply_text(
            "💖 حمایت از ما\n\nاگر این ربات برات مفید بود، اون رو به دوستانت معرفی کن.\n\nممنون از حمایتت 🌹\n\nاکر دوست داشتی می‌تونی از لینک زیر ما رو دونیت کنی:\nhttps://daramet.com/MZTDL",
            reply_markup=back_menu(),
        )

    elif text == "🛠️ پشتیبانی":
        await update.message.reply_text(
            "📞 پشتیبانی\n\nاگر نیاز به کمک داری، می‌تونی از طریق این آیدی ما تماس بگیری.\n\nما همیشه برای کمک به تو آماده‌ایم! 🙌\n@MZBOTS_Support",
            reply_markup=back_menu(),
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
            reply_markup=back_menu(),
        )

    elif text == "👥 افزودن به گروه (درحال توسعه)":
        await update.message.reply_text(
            "این بخش در حال توسعه است...", reply_markup=back_menu()
        )

    elif text == "🏠 بازگشت به خانه":
        await update.message.reply_text("منوی اصلی", reply_markup=main_menu())


async def handle_links(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    joined = await is_joined(context.bot, user_id)
    if not joined:
        await update.message.reply_text(
            "برای استفاده از ربات ابتدا عضو کانال شوید!\nو سپس دوباره /start را بزنید!",
            reply_markup=join_channel_keyboard(),
        )
        return
    text = update.message.text

    if not text.startswith("http"):
        return
    platform = detect_platform(text)

    if platform == "youtube":

        save_url(update.effective_user.id, text)

        try:

            info = get_video_info(text)

            if is_shorts(text):

                await update.message.reply_photo(
                    photo=info["thumbnail"],
                    caption=info["title"],
                    reply_markup=shorts_keyboard(),
                )

            else:

                await update.message.reply_photo(
                    photo=info["thumbnail"],
                    caption=info["title"],
                    reply_markup=youtube_keyboard(),
                )

        except Exception:

            await update.message.reply_text("❌ دانلود این محتوا امکان‌پذیر نیست.")

    elif platform == "instagram":

        save_url(update.effective_user.id, text)

        info = get_instagram_info(text)

        await update.message.reply_photo(
            photo=info["thumbnail"],
            caption=info["title"],
            reply_markup=instagram_keyboard(),
        )

    elif platform == "tiktok":

        save_url(update.effective_user.id, text)

        info = get_tiktok_info(text)

        await update.message.reply_photo(
            photo=info["thumbnail"],
            caption=info["title"],
            reply_markup=tiktok_keyboard(),
        )

    elif platform == "soundcloud":

        save_url(update.effective_user.id, text)

        info = get_soundcloud_info(text)

        await update.message.reply_photo(
            photo=info["thumbnail"],
            caption=info["title"],
            reply_markup=soundcloud_keyboard(),
        )

    elif platform == "spotify":

        await update.message.reply_text("🚧 دانلود از Spotify در حال توسعه است.")


async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    if user_id in active_download:

        await query.message.reply_text("⏳ دانلود قبلی شما هنوز تمام نشده است.")
        return

    data = query.data

    if data == "youtube_mp3":

        url = get_url(user_id)

        if not url:

            await query.message.reply_text("لینکی پیدا نشد.")
            return

        if detect_platform(url) != "youtube":

            await query.message.reply_text("❌ این دکمه منقضی شده است.")
            return
        status_msg = await query.message.reply_text("⏳ در حال ورود به صف...")

        file_path = None

        async def process_youtube_mp3():

            start_time = time.time()

            file_path = None

            try:

                file_path = await asyncio.to_thread(
                    download_mp3,
                    url,
                    user_id,
                )

                duration = get_audio_duration(file_path)

                if duration <= 1800:

                    with open(file_path, "rb") as audio:

                        await query.message.reply_audio(audio=audio)

                else:

                    parts = split_mp3(file_path, 1200)

                    for index, part in enumerate(parts, start=1):

                        with open(part, "rb") as audio:

                            await query.message.reply_audio(
                                audio=audio,
                                caption=f"Part {index}",
                            )

            finally:

                if file_path and os.path.exists(file_path):

                    os.remove(file_path)

                elapsed = time.time() - start_time

                average_download_times.append(elapsed)

                if len(average_download_times) > 20:

                    average_download_times.pop(0)

                active_download.discard(user_id)

        job = {
            "user_id": user_id,
            "task": process_youtube_mp3,
        }

        await download_queue.put(job)

        asyncio.create_task(
            queue_status_loop(
                user_id,
                status_msg,
            )
        )

        await query.message.reply_text("✅ درخواست دانلود ثبت شد.")

        try:

            async with download_semaphore:

                file_path = await asyncio.to_thread(download_mp3, url, user_id)

            duration = get_audio_duration(file_path)

            if duration <= 1800:

                with open(file_path, "rb") as audio:

                    await query.message.reply_audio(audio=audio)

            else:

                await query.message.reply_text("📦 فایل طولانی است، در حال تقسیم...")

                parts = split_mp3(file_path, 1200)

                for index, part in enumerate(parts, start=1):

                    try:

                        with open(part, "rb") as audio:

                            await query.message.reply_audio(
                                audio=audio, caption=f"Part {index}"
                            )

                    finally:

                        if os.path.exists(part):
                            os.remove(part)

            await msg.delete()

        except Exception as e:

            print(e)

            await query.message.reply_text(
                "❌ دانلود ناموفق بود.\n\n(این خطا ممکن است به‌دلیل سرعت اینترنت باشد، چند دقیقه صبر کنید اگر فایل ارسال نشد مجدد تلاش کنید.)"
            )

        finally:

            if file_path and os.path.exists(file_path):
                os.remove(file_path)

            active_download.discard(user_id)

    elif data.startswith("youtube_"):
        url = get_url(user_id)

        if not url:
            await query.message.reply_text("لینکی پیدا نشد.")
            return

        if detect_platform(url) != "youtube":
            await query.message.reply_text("❌ این دکمه منقضی شده است.")
            return

        active_download.add(user_id)

        quality = data.split("_")[1]

        msg = await query.message.reply_text(f"⏳ دانلود {quality}p...")

        file_path = None

        try:

            async with download_semaphore:

                file_path = await asyncio.to_thread(
                    download_video, url, user_id, quality
                )

            await query.message.reply_text("📦 در حال تقسیم ویدیو...")

            parts = split_video_by_size(file_path, 30)

            for index, part in enumerate(parts, start=1):

                try:

                    with open(part, "rb") as video:

                        await query.message.reply_video(
                            video=video,
                            supports_streaming=True,
                            caption=f"Part {index}",
                        )

                finally:

                    if part != file_path and os.path.exists(part):

                        os.remove(part)

            await msg.delete()

        except Exception as e:

            await query.message.reply_text(
                "❌ دانلود ناموفق بود.\n\n(این خطا ممکن است به‌دلیل سرعت اینترنت باشد، چند دقیقه صبر کنید اگر فایل ارسال نشد مجدد تلاش کنید.)"
            )

        finally:

            if file_path and os.path.exists(file_path):
                os.remove(file_path)

            active_download.discard(user_id)

    elif data.startswith("shorts_"):

        url = get_url(user_id)

        if not url:

            await query.message.reply_text("لینکی پیدا نشد.")
            return

        if detect_platform(url) != "youtube":

            await query.message.reply_text("❌ این دکمه منقضی شده است.")
            return
        active_download.add(user_id)
        quality = data.split("_")[1]

        if quality == "mp3":

            msg = await query.message.reply_text("⏳ در حال دانلود MP3...")

            file_path = None

            try:

                async with download_semaphore:

                    file_path = await asyncio.to_thread(download_mp3, url, user_id)

                with open(file_path, "rb") as audio:

                    await query.message.reply_audio(audio=audio)

                await msg.delete()

            except Exception as e:

                print(e)

                await query.message.reply_text(
                    "❌ دانلود ناموفق بود.\n\n(این خطا ممکن است به‌دلیل سرعت اینترنت باشد، چند دقیقه صبر کنید اگر فایل ارسال نشد مجدد تلاش کنید.)"
                )

            finally:

                if file_path and os.path.exists(file_path):
                    os.remove(file_path)

                active_download.discard(user_id)

        else:

            msg = await query.message.reply_text(f"⏳ دانلود {quality}p...")

            file_path = None

            try:

                async with download_semaphore:

                    file_path = await asyncio.to_thread(
                        download_video, url, user_id, quality
                    )

                with open(file_path, "rb") as video:

                    await query.message.reply_video(
                        video=video, supports_streaming=True
                    )

                await msg.delete()

            except Exception as e:

                print(e)

                await query.message.reply_text(
                    "❌ دانلود ناموفق بود.\n\n(این خطا ممکن است به‌دلیل سرعت اینترنت باشد، چند دقیقه صبر کنید اگر فایل ارسال نشد مجدد تلاش کنید.)"
                )

            finally:

                if file_path and os.path.exists(file_path):
                    os.remove(file_path)

                active_download.discard(user_id)

    elif data == "instagram_download":

        url = get_url(user_id)

        if detect_platform(url) != "instagram":

            await query.message.reply_text(
                "❌ این دکمه مربوط به آخرین لینک اینستاگرام شما نیست."
            )
            return
        active_download.add(user_id)
        msg = await query.message.reply_text("⏳ در حال دانلود...")

        file_path = None

        try:

            async with download_semaphore:

                file_path = await asyncio.to_thread(download_instagram, url, user_id)

            with open(file_path, "rb") as video:

                await query.message.reply_video(video=video, supports_streaming=True)

            await msg.delete()

        except Exception as e:

            print(e)

            await query.message.reply_text(str(e))

        finally:

            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            active_download.discard(user_id)

    elif data == "tiktok_download":

        url = get_url(user_id)
        active_download.add(user_id)
        msg = await query.message.reply_text("⏳ در حال دانلود...")

        file_path = None

        try:

            async with download_semaphore:

                file_path = await asyncio.to_thread(download_tiktok, url, user_id)

            with open(file_path, "rb") as video:

                await query.message.reply_video(video=video, supports_streaming=True)

            await msg.delete()

        except Exception as e:

            print(e)

            await query.message.reply_text(
                "❌ دانلود ناموفق بود.\n\n(این خطا ممکن است به‌دلیل سرعت اینترنت باشد، چند دقیقه صبر کنید اگر فایل ارسال نشد مجدد تلاش کنید.)"
            )

        finally:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            active_download.discard(user_id)

    elif data == "soundcloud_mp3":

        url = get_url(user_id)
        active_download.add(user_id)
        msg = await query.message.reply_text("⏳ در حال دانلود...")

        file_path = None

        try:

            async with download_semaphore:

                file_path = await asyncio.to_thread(download_soundcloud, url, user_id)

            with open(file_path, "rb") as audio:

                await query.message.reply_audio(audio=audio)

            await msg.delete()

        except Exception as e:

            print(e)

            await query.message.reply_text(
                "❌ دانلود ناموفق بود.\n\n(این خطا ممکن است به‌دلیل سرعت اینترنت باشد، چند دقیقه صبر کنید اگر فایل ارسال نشد مجدد تلاش کنید.)"
            )

        finally:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            active_download.discard(user_id)


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
    broadcast_mode.add(update.effective_user.id)

    await update.message.reply_text("پیام همگانی را ارسال کن:")


async def start_workers(app):
    for i in range(3):
        asyncio.create_task(download_worker(i + 1))


def main():
    create_tables()

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(10000)
        .read_timeout(10000)
        .build()
    )

    app.post_init = start_workers

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buttons))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_links), group=1
    )
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(CommandHandler("admin", admin_pannel))
    app.add_handler(CommandHandler("broadcast", broadcast))

    print("Bot Started...")

    app.run_polling()


if __name__ == "__main__":
    main()
