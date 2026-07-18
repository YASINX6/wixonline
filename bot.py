import telebot
from telebot import types
import sqlite3

# توکن رسمی ربات شما
API_TOKEN = '8648815822:AAHso-sAPat6S_P8yVWSBW0cN_0yR0wijkM'
bot = telebot.TeleBot(API_TOKEN)

# آیدی عددی تلگرام شما جهت دریافت تاییدیه کشورها
ADMIN_ID = 7961155790
ADMIN_USERNAME = "EXLUG" 

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

# پایگاه داده کامل کشورها و گروهک‌ها (بدون کاراکتر زیرخط در کدها)
GAME_ENTITIES = {
    "europe": {
        "usa": {"name": "🇺🇸 آمریکا", "price": "۲۰۰,۰۰۰ تومان", "vip": True},
        "uk": {"name": "🇬🇧 بریتانیا", "price": "۱۰۰,۰۰۰ تومان", "vip": True},
        "france": {"name": "🇫🇷 فرانسه", "price": "۹۰,۰۰۰ تومان", "vip": True},
        "germany": {"name": "🇩🇪 آلمان", "price": "۸۵,۰۰۰ تومان", "vip": True},
        "italy": {"name": "🇮🇹 ایتالیا", "price": None, "vip": False},
        "spain": {"name": "🇪🇸 اسپانیا", "price": None, "vip": False},
        "canada": {"name": "🇨🇦 کانادا", "price": None, "vip": False},
        "brazil": {"name": "🇧🇷 برزیل", "price": None, "vip": False},
        "poland": {"name": "🇵🇱 لهستان", "price": None, "vip": False},
        "austria": {"name": "🇦🇹 اتریش", "price": None, "vip": False},
        "norway": {"name": "🇳🇴 نروژ", "price": None, "vip": False},
        "sweden": {"name": "🇸🇪 سوئد", "price": None, "vip": False},
        "ukraine": {"name": "🇺🇦 اوکراین", "price": None, "vip": False},
        "portugal": {"name": "🇵🇹 پرتغال", "price": None, "vip": False},
        "skorea": {"name": "🇰🇷 کره جنوبی", "price": None, "vip": False},
    },
    "asia": {
        "russia": {"name": "😈 روسیه", "price": "۱۷۰,۰۰۰ تومان", "vip": True},
        "china": {"name": "🇨🇳 چین", "price": "۱۵۰,۰۰۰ تومان", "vip": True},
        "india": {"name": "🇮🇳 هند", "price": "۱۲۰,۰۰۰ تومان", "vip": True},
        "iran": {"name": "🇮🇷 ایران", "price": "۵۰,۰۰۰ تومان", "vip": True},
        "israel": {"name": "🇮🇱 اسرائیل", "price": "۵۰,۰۰۰ تومان", "vip": True},
        "afghanistan": {"name": "🇦🇫 افغانستان", "price": None, "vip": False},
        "iraq": {"name": "🇮🇶 عراق", "price": None, "vip": False},
        "lebanon": {"name": "🇱🇧 لبنان", "price": None, "vip": False},
        "yemen": {"name": "🇾🇪 انصارالله یمن", "price": None, "vip": False},
        "turkey": {"name": "🇹🇷 ترکیه", "price": None, "vip": False},
        "saudi": {"name": "🇸🇦 عربستان سعودی", "price": None, "vip": False},
        "uae": {"name": "🇦🇪 امارات متحده عربی", "price": None, "vip": False},
        "belarus": {"name": "🇧🇾 بلاروس", "price": None, "vip": False},
        "nkorea": {"name": "🇰🇵 کره شمالی", "price": None, "vip": False},
        "taiwan": {"name": "🇹🇼 تایوان", "price": None, "vip": False},
        "pakistan": {"name": "🇵🇰 پاکستان", "price": None, "vip": False},
    },
    "africa": {
        "libya": {"name": "🇱🇾 لیبی", "price": None, "vip": False},
        "egypt": {"name": "🇪🇬 مصر", "price": None, "vip": False},
        "nigeria": {"name": "🇳🇬 نیجریه", "price": None, "vip": False},
        "morocco": {"name": "🇲🇦 مراکش", "price": None, "vip": False},
    },
    "groups": {
        "irgc": {"name": "🔴 سپاه پاسداران", "price": "۶۰,۰۰۰ تومان", "vip": True},
        "wagner": {"name": "💀 گروه واغنر", "price": "۶۰,۰۰۰ تومان", "vip": True},
        "qaeda": {"name": "🏴 القاعده", "price": None, "vip": False},
        "daesh": {"name": "🏴‍☠️ داعش", "price": None, "vip": False},
        "taliban": {"name": "🪖 طالبان", "price": None, "vip": False},
        "hizblebanon": {"name": "💛 حزب‌الله لبنان", "price": None, "vip": False},
        "kurdistan": {"name": "☀️ حزب کردستان", "price": None, "vip": False},
    }
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    player = get_player(user_id)
    if player and player[3] == 'approved':
        bot.send_message(chat_id, f"⚔️ **فرمانده! شما قبلاً عضو شده‌اید و نقش شما تأیید شده است:**\n🎭 جبهه شما: **{player[2]}**", parse_mode="Markdown")
        return

    welcome_text = (
        "🌍 **به بزرگترین شبیه‌ساز جنگ جهانی سوم (Last Banner) خوش آمدید!** 🌍\n\n"
        "آیا هوش و ذکاوت رهبری یک ابرقدرت، یک کشور در حال توسعه یا یک گروهک چریکی قدرتمند را در بحبوحه‌ی مدرن‌ترین جنگ تاریخ دارید؟\n"
        "در این سیزن، همه‌چیز دستخوش تغییر شده است؛ از تحلیل رول‌ها گرفته تا انبار تجهیزات مدرن، سیستم سوددهی خودکارِ سر وقت و سیستم‌های خرید نظامی، همگی به صورت ۱۰۰٪ هوشمند روی همین ربات مدیریت می‌شوند. نیروی انسانی، تانک‌ها، جت‌ها و موشک‌های بالستیک شما منتظر اولین دستور شما هستند.\n\n"
        "در این بازی، ربات ما همه کارها را به صورت کاملاً خودکار، آنی و بدون هیچ معطلی با بالاترین سرعت برای شما پردازش و ثبت می‌کند. اتاق فرماندهی شما اینجاست و همه‌چیز در کسری از ثانیه تحت کنترل ربات اجرا خواهد شد.\n\n"
        "👇 **همین حالا جبهه خود را انتخاب کنید:** برای شروع، روی دکمه زیر ضربه بزنید:"
    )
    
    markup = types.InlineKeyboardMarkup()
    btn_select = types.InlineKeyboardButton("🌍 رزرو کشور یا گروهک", callback_data="main_menu")
    markup.add(btn_select)
    bot.send_message(chat_id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# منوی اصلی دسته‌ب بندی‌ها
@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def main_menu(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    text = "🚩 **انتخاب کنید که قصد رزرو جبهه در کدام منطقه را دارید:**"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🏛️ اروپا و آمریکا", callback_data="cat_europe")
    btn2 = types.InlineKeyboardButton("🌏 آسیا", callback_data="cat_asia")
    btn3 = types.InlineKeyboardButton("🌍 آفریقا", callback_data="cat_africa")
    btn4 = types.InlineKeyboardButton("🪖 گروهک‌ها", callback_data="cat_groups")
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup, parse_mode="Markdown")

# نمایش لیست جبهه‌های یک دسته خاص
@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def show_category(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    category_code = call.data.replace("cat_", "")
    
    titles = {"europe": "🏛️ اروپا و آمریکا", "asia": "🌏 آسیا", "africa": "🌍 آفریقا", "groups": "🪖 گروهک‌ها"}
    text = f"👇 **لیست جبهه‌های موجود در بخش {titles[category_code]}:**\n\nانتخاب کنید:"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    
    for code, info in GAME_ENTITIES[category_code].items():
        if info["vip"]:
            btn_text = f"⭐ {info['name']} (VIP)"
        else:
            btn_text = info["name"]
            
        btn = types.InlineKeyboardButton(btn_text, callback_data=f"select_{category_code}_{code}")
        buttons.append(btn)
        
    markup.add(*buttons)
    btn_back = types.InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")
    markup.add(btn_back)
    
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup, parse_mode="Markdown")

# پردازش انتخاب نهایی یک جبهه
@bot.callback_query_handler(func=lambda call: call.data.startswith("select_"))
def process_selection(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.from_user.id
    username = call.from_user.username or "ندارد"
    
    # تفکیک دقیق داده با ۲ کاراکتر زیرخط اول
    parts = call.data.split("_", 2)
    category = parts[1]
    entity_code = parts[2]
    
    entity_info = GAME_ENTITIES[category][entity_code]
    name = entity_info["name"]
    
    if entity_info["vip"]:
        text = (
            f"💎 **درخواست رزرو جبهه ویژه (VIP): {name}**\n\n"
            f"💰 **هزینه رزرو ویژه:** {entity_info['price']}\n\n"
            "⚠️ جهت پرداخت هزینه رزرو و نهایی کردن خرید، روی دکمه زیر کلیک کرده و رسید و نام جبهه را برای مالک ارسال کنید تا اکانت شما فعال شود:"
        )
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_pay = types.InlineKeyboardButton("💬 پیام به مالک جهت خرید و فعالسازی", url=f"https://t.me/{ADMIN_USERNAME}")
        btn_back = types.InlineKeyboardButton("🔙 بازگشت به منو", callback_data=f"cat_{category}")
        markup.add(btn_pay, btn_back)
        
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup, parse_mode="Markdown")
        
    else:
        set_pending_player(user_id, username, name)
        
        bot.edit_message_text(
            chat_id=chat_id, 
            message_id=message_id, 
            text=f"⏳ **درخواست رزرو جبهه {name} ثبت شد و در حال انتظار برای تایید مالک بازی می‌باشد.**\n\nنتیجه به زودی از همین طریق به شما اعلام می‌شود.",
            reply_markup=None,
            parse_mode="Markdown"
        )
        
        admin_markup = types.InlineKeyboardMarkup()
        btn_approve = types.InlineKeyboardButton("✅ تایید درخواست", callback_data=f"admin_approve_{user_id}")
        btn_reject = types.InlineKeyboardButton("❌ رد درخواست", callback_data=f"admin_reject_{user_id}")
        admin_markup.add(btn_approve, btn_reject)
        
        admin_text = (
            f"📥 **درخواست رزرو جبهه عادی جدید!**\n\n"
            f"👤 **کاربر:** @{username}\n"
            f"🆔 **آیدی: ** `{user_id}`\n"
            f"🌍 **جبهه درخواستی:** {name}\n\n"
            f"آیا این درخواست را تایید می‌کنید؟"
        )
        
        try:
            bot.send_message(ADMIN_ID, admin_text, reply_markup=admin_markup, parse_mode="Markdown")
        except Exception as e:
            print(f"خطا در ارسال پیام به ادمین: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_decision(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ شما مالک بازی نیستید!", show_alert=True)
        return
        
    action = call.data.replace("admin_", "")
    
    if action.startswith("approve_"):
        target_user_id = int(action.replace("approve_", ""))
        player = get_player(target_user_id)
        if player:
            approve_player(target_user_id)
            try:
                bot.send_message(target_user_id, f"🎉 **تبریک فرمانده!**\nدرخواست شما برای رهبری **{player[2]}** توسط مالک بازی تایید شد.\n\nبه زودی سیزن آغاز می‌شود!")
            except Exception:
                pass
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"✅ درخواست کاربر `{target_user_id}` برای جبهه **{player[2]}** با موفقیت **تایید** شد.", reply_markup=None, parse_mode="Markdown")
            
    elif action.startswith("reject_"):
        target_user_id = int(action.replace("reject_", ""))
        player = get_player(target_user_id)
        if player:
            reject_player(target_user_id)
            try:
                bot.send_message(target_user_id, f"❌ متاسفانه درخواست شما برای رزرو جبهه **{player[2]}** رد شد.")
            except Exception:
                pass
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"❌ درخواست کاربر `{target_user_id}` برای جبهه **{player[2]}** **رد** شد.", reply_markup=None, parse_mode="Markdown")

bot.polling()
