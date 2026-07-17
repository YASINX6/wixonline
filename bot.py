import telebot
from telebot import types
import sqlite3

# توکن رسمی ربات شما
API_TOKEN = '8648815822:AAHso-sAPat6S_P8yVWSBW0cN_0yR0wijkM'
bot = telebot.TeleBot(API_TOKEN)

# ⚠️ آیدی عددی تلگرام خودت را اینجا بگذار (مثلاً 123456789) تا درخواست‌های تایید برای تو ارسال شوند.
ADMIN_ID = 8648815822

# --- بخش دیتابیس ---
def init_db():
    conn = sqlite3.connect('wixonline.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            role TEXT,
            status TEXT DEFAULT 'pending'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_player(user_id):
    conn = sqlite3.connect('wixonline.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    player = cursor.fetchone()
    conn.close()
    return player

def set_pending_player(user_id, username, role):
    conn = sqlite3.connect('wixonline.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO players (user_id, username, role, status)
        VALUES (?, ?, ?, 'pending')
    ''', (user_id, username, role))
    conn.commit()
    conn.close()

def approve_player(user_id):
    conn = sqlite3.connect('wixonline.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET status = 'approved' WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def reject_player(user_id):
    conn = sqlite3.connect('wixonline.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
# ------------------

# لیست قیمت کشورها
COUNTRY_PRICES = {
    "iran": ("🇮🇷 ایران", "۶۰,۰۰۰ تومان"),
    "saudi": ("🇸🇦 عربستان سعودی", "۶۰,۰۰۰ تومان"),
    "israel": ("🇮🇱 اسرائیل", "۵۰,۰۰۰ تومان"),
    "turkey": ("🇹🇷 ترکیه", "۵۰,۰۰۰ تومان"),
    "usa": ("🇺🇸 آمریکا", "۵۰,۰۰۰ تومان")
}

# لیست گروهک‌ها
GROUPS = {
    "hizb": "🪖 حزب‌الله لبنان",
    "hamas": "🔺 حماس فلسطین",
    "yemen": "🇾🇪 انصارالله یمن",
    "taliban": "🦅 طالبان افغانستان",
    "jehad": "🏴 جهاد اسلامی فلسطین",
    "hashd": "🦊 حشد الشعبی عراق",
    "sdf": "🛡️ نیروهای دموکراتیک سوریه (SDF)",
    "qaeda": "🐍 القاعده شبه‌جزیره",
    "qassam": "🛻 گردان‌های قسام",
    "pkk": "🐆 حزب کارگران کردستان (PKK)"
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    player = get_player(user_id)
    if player and player[3] == 'approved':
        bot.send_message(chat_id, f"⚔️ فرمانده! شما قبلاً عضو شده‌اید و نقش شما تأیید شده است: **{player[2]}**", parse_mode="Markdown")
        return

    # متن انتخابی سوم شما (شیک و حماسی)
    welcome_text = (
        "🔥 **به اولین سیزن WIXON LINE خوش آمدید!** 🔥\n\n"
        "این گیم شبیه‌ساز واقعی تحولات پرآشوب خاورمیانه با محوریت نبرد مقتدرانه **گروهک‌ها** است! "
        "دوره جنگ‌های کلاسیک و تکراری تمام شده؛ حالا زمان جنگ‌های چریکی، شبیخون‌های شبانه و معاملات پنهانی در بازار سیاه است. "
        "در این بازی، ربات ما همه کارها را به صورت کاملاً خودکار و آنی برای شما پردازش و ثبت می‌کند.\n\n"
        "تفنگت را مسلح کن و برای رهبری جبهه خود آماده شو!\n\n"
        "👇 **فرصت را از دست نده:**\n"
        "برای رزرو کردن کشور یا گروهک روی دکمه زیر کلیک کنید:"
    )
    
    markup = types.InlineKeyboardMarkup()
    btn_select = types.InlineKeyboardButton("🌍 رزرو کشور یا گروهک", callback_data="main_menu")
    markup.add(btn_select)
    
    bot.send_message(chat_id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# منوی اصلی انتخاب کشور یا گروهک
@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def main_menu(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    text = "🚩 **انتخاب کنید که قصد رزرو کدام جبهه را دارید:**"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_countries = types.InlineKeyboardButton("🏛️ رزرو کشورها (پولی)", callback_data="list_countries")
    btn_groups = types.InlineKeyboardButton("🪖 رزرو گروهک‌ها (رایگان/تاییدی)", callback_data="list_groups")
    markup.add(btn_countries, btn_groups)
    
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup, parse_mode="Markdown")

# لیست کشورها
@bot.callback_query_handler(func=lambda call: call.data == "list_countries")
def list_countries(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    text = "🏛️ **لیست کشورهای موجود جهت رزرو:**\n\nانتخاب کنید:"
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for code, (name, price) in COUNTRY_PRICES.items():
        btn = types.InlineKeyboardButton(f"{name} 👈 {price}", callback_data=f"pay_{code}")
        markup.add(btn)
        
    btn_back = types.InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")
    markup.add(btn_back)
    
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup, parse_mode="Markdown")

# منوی پرداخت برای کشورها
@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
def pay_country(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    country_code = call.data.replace("pay_", "")
    
    name, price = COUNTRY_PRICES[country_code]
    
    text = (
        f"💳 **درخواست رزرو کشور: {name}**\n"
        f"💰 **هزینه رزرو:** {price}\n\n"
        "جهت پرداخت هزینه کشور و نهایی کردن رزرو، روی دکمه زیر کلیک کرده و رسید پرداخت را ارسال کنید:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_pay = types.InlineKeyboardButton("💬 پیام به پشتیبانی جهت پرداخت", url="https://t.me/EXLUG")
    btn_back = types.InlineKeyboardButton("🔙 بازگشت به لیست کشورها", callback_data="list_countries")
    markup.add(btn_pay, btn_back)
    
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup, parse_mode="Markdown")

# لیست گروهک‌ها
@bot.callback_query_handler(func=lambda call: call.data == "list_groups")
def list_groups(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    text = "🪖 **لیست گروهک‌های موجود جهت رزرو:**\n\nانتخاب کنید:"
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    buttons = []
    for code, name in GROUPS.items():
        btn = types.InlineKeyboardButton(name, callback_data=f"req_{code}")
        buttons.append(btn)
        
    markup.add(*buttons)
    btn_back = types.InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")
    markup.add(btn_back)
    
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup, parse_mode="Markdown")

# ثبت درخواست گروهک و ارسال برای ادمین
@bot.callback_query_handler(func=lambda call: call.data.startswith("req_"))
def request_group(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.from_user.id
    username = call.from_user.username or "ندارد"
    group_code = call.data.replace("req_", "")
    
    group_name = GROUPS[group_code]
    
    # ذخیره درخواست به صورت در حال انتظار در دیتابیس
    set_pending_player(user_id, username, group_name)
    
    # پیام به بازیکن
    bot.edit_message_text(
        chat_id=chat_id, 
        message_id=message_id, 
        text=f"⏳ **درخواست رزرو گروهک {group_name} ثبت شد و در حال انتظار برای تایید مالک بازی می‌باشد.**\n\nنتیجه به زودی از همین طریق به شما اعلام می‌شود.",
        reply_markup=None,
        parse_mode="Markdown"
    )
    
    # ارسال دکمه‌های تایید/رد به پیوی مالک (تو)
    admin_markup = types.InlineKeyboardMarkup()
    btn_approve = types.InlineKeyboardButton("✅ تایید", callback_data=f"admin_approve_{user_id}")
    btn_reject = types.InlineKeyboardButton("❌ رد درخواست", callback_data=f"admin_reject_{user_id}")
    admin_markup.add(btn_approve, btn_reject)
    
    admin_text = (
        f"📥 **درخواست رزرو گروهک جدید!**\n\n"
        f"👤 **کاربر:** @{username}\n"
        f"🆔 **آیدی عددی:** `{user_id}`\n"
        f"🪖 **گروهک درخواستی:** {group_name}\n\n"
        f"آیا این درخواست را تایید می‌کنید؟"
    )
    
    try:
        bot.send_message(ADMIN_ID, admin_text, reply_markup=admin_markup, parse_mode="Markdown")
    except Exception as e:
        print(f"خطا در ارسال پیام به ادمین: {e}. مطمئن شوید ادمین ربات را استارت کرده باشد.")

# پردازش تصمیمات ادمین (تایید یا رد)
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_decision(call):
    # بررسی اینکه فقط خودت بتوانی دکمه‌های تایید را بزنی
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ شما مالک بازی نیستید!", show_alert=True)
        return
        
    action = call.data.replace("admin_", "")
    
    if action.startswith("approve_"):
        target_user_id = int(action.replace("approve_", ""))
        player = get_player(target_user_id)
        if player:
            approve_player(target_user_id)
            # اعلام به بازیکن
            try:
                bot.send_message(target_user_id, f"🎉 **تبریک فرمانده!**\nدرخواست شما برای رهبری گروهک **{player[2]}** توسط مالک بازی تایید شد.\n\nبه زودی سیزن بازی آغاز می‌شود!")
            except Exception:
                pass
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"✅ درخواست کاربر `{target_user_id}` با موفقیت **تایید** شد.", reply_markup=None, parse_mode="Markdown")
            
    elif action.startswith("reject_"):
        target_user_id = int(action.replace("reject_", ""))
        player = get_player(target_user_id)
        if player:
            reject_player(target_user_id)
            # اعلام به بازیکن
            try:
                bot.send_message(target_user_id, f"❌ متاسفانه درخواست شما برای رزرو گروهک **{player[2]}** رد شد.")
            except Exception:
                pass
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"❌ درخواست کاربر `{target_user_id}` **رد** شد.", reply_markup=None, parse_mode="Markdown")

bot.polling()
