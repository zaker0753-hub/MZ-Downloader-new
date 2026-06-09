from telegram import ReplyKeyboardMarkup

def main_menu():
    keybpard = [
         ["📥 دانلود", "❤️ حمایت"],
        ["🛠️ پشتیبانی", "📖 راهنما"],
        ["👥 افزودن به گروه (درحال توسعه)"]
    ]
    return ReplyKeyboardMarkup(
        keybpard,
        resize_keyboard=True
    )

def back_menu():
    keyboard = [
        ["🏠 بازگشت به خانه"]
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )