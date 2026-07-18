import telebot
from telebot import types
import sqlite3
import sys
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# حل مشکل مسیردهی پایتون در هاست رندر برای پوشه‌ها
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔄 Starting initialization...")

try:
    # تلاش برای ایمپورت کردن دیتای نظامی با مدیریت خطا
    print("🔄 Trying to import military data...")
    if os.path.exists("data/military_data.py") or os.path.exists("data"):
        from data.military_data import get_military_info
        print("✅ Military data imported successfully from data folder.")
    else:
        from military_data import get_military_info
        print("✅ Military data imported successfully from root folder.")
except Exception as e:
    print(f"⚠️ IMPORT ERROR: {e}")
    def get_military_info(country_code):
        return "❌ خطا: فایل داده‌های نظامی یافت نشد. لطفا مسیر پوشه را چک کنید."

# توکن رسمی ربات شما
API_TOKEN = '8648815822:AAH3uJ4aN_oCGP_ckppYNQgasBVkGk5_OzM'
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 7961155790
ADMIN_USERNAME = "EXLUG" 

# --- بخش دیتابیس با مدیریت خطای قفل شدن ---
def init_db():
    try:
        conn = sqlite3.connect('wixonline.db', timeout=10)
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
        print("✅ Database initialized successfully.")
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")

init_db()

def get_player(user_id):
    try:
        conn = sqlite3.connect('wixonline.db', timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
        player = cursor.fetchone()
        conn.close()
        return player
    except:
        return None

def set_pending_player(user_id, username, role):
    try:
        conn = sqlite3.connect('wixonline.db', timeout=10)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO players (user_id, username, role, status)
            VALUES (?, ?, ?, 'pending')
        ''', (user_id, username, role))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ DB INSERT ERROR: {e}")

def approve_player(user_id):
    try:
        conn = sqlite3.connect('wixonline.db', timeout=10)
        cursor = conn.cursor()
        cursor.execute("UPDATE players SET status = 'approved' WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    except:
        pass

def reject_player(user_id):
    try:
        conn = sqlite3.connect('wixonline.db', timeout=10)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM players WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    except:
        pass
# ------------------

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
        "india": {"name": "🇮🇳 هند", "price": "۱۲۰,۰۰0 تومان", "vip": True},
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

def get_military_menu():
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🇺🇸 آمریکا (VIP)", callback_data="mil_usa"), types.InlineKeyboardButton("🇷🇺 روسیه (VIP)", callback_data="mil_russia"))
    markup.row(types.InlineKeyboardButton("🇨🇳 چین (VIP)", callback_data="mil_china"), types.InlineKeyboardButton("🇬🇧 بریتانیا (VIP)", callback_data="mil_uk"))
    markup.row(types.InlineKeyboardButton("🇫🇷 فرانسه (VIP)", callback_data="mil_france"), types.InlineKeyboardButton("🇩🇪 آلمان (VIP)", callback_data="mil_germany"))
    markup.row(types.InlineKeyboardButton("🇮🇳 هند (VIP)", callback_data="mil_india"), types.InlineKeyboardButton("🇮🇱 اسرائیل (VIP)", callback_data="mil_israel"))
    markup.row(types.InlineKeyboardButton("🟢 ارتش ایران", callback_data="mil_iran"), types.InlineKeyboardButton("🔴 سپاه پاسداران", callback_data="mil_irgc"))
    markup.row(types.InlineKeyboardButton("💀 سازمان واگنر", callback_data="mil_wagner"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        player = get_player(message.from_user.id)
        if player and player[3] == 'approved':
            bot.send_message(message.chat.id, f"⚔️ **فرمانده! شما قبلاً عضو شده‌اید:**\n🎭 جبهه شما: **{player[2]}**", parse_mode="Markdown")
            return
        welcome_text = "🌍 **به بزرگترین شبیه‌ساز جنگ جهانی سوم خوش آمدید!**\n👇 جبهه خود را انتخاب کنید:"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🌍 رزرو کشور یا گروهک", callback_data="main_menu"))
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        print(f"Error in start command: {e}")

@bot.message_handler(commands=['military'])
def send_military_hub(message):
    welcome_text = "⚔️ **به سامانه اطلاعات استراتژیک خوش آمدید**\nانتخاب کنید:"
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_military_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def main_menu(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🏛️ اروپا و آمریکا", callback_data="cat_europe"),
        types.InlineKeyboardButton("🌏 آسیا", callback_data="cat_asia"),
        types.InlineKeyboardButton("🌍 آفریقا", callback_data="cat_africa"),
        types.InlineKeyboardButton("🪖 گروهک‌ها", callback_data="cat_groups")
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🚩 **انتخاب کنید که قصد رزرو جبهه در کدام منطقه را دارید:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def show_category(call):
    category_code = call.data.replace("cat_", "")
    titles = {"europe": "🏛️ اروپا و آمریکا", "asia": "🌏 آسیا", "africa": "🌍 آفریقا", "groups": "🪖 گروهک‌ها"}
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for code, info in GAME_ENTITIES[category_code].items():
        btn_text = f"⭐ {info['name']} (VIP)" if info["vip"] else info["name"]
        buttons.append(types.InlineKeyboardButton(btn_text, callback_data=f"select_{category_code}_{code}"))
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"👇 **لیست جبهه‌های موجود در بخش {titles[category_code]}:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("select_"))
def process_selection(call):
    try:
        parts = call.data.split("_", 2)
        category, entity_code = parts[1], parts[2]
        entity_info = GAME_ENTITIES[category][entity_code]
        name = entity_info["name"]
        
        if entity_info["vip"]:
            text = f"💎 **درخواست رزرو جبهه ویژه (VIP): {name}**\n\n💰 **هزینه رزرو ویژه:** {entity_info['price']}\n\n⚠️ جهت پرداخت به مالک پیام دهید:"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("💬 پیام به مالک", url=f"https://t.me/{ADMIN_USERNAME}"), types.InlineKeyboardButton("🔙 بازگشت", callback_data=f"cat_{category}"))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")
        else:
            set_pending_player(call.from_user.id, call.from_user.username or "ندارد", name)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"⏳ **درخواست رزرو جبهه {name} ثبت شد و در انتظار تایید است.**")
            
            admin_markup = types.InlineKeyboardMarkup()
            admin_markup.add(types.InlineKeyboardButton("✅ تایید", callback_data=f"admin_approve_{call.from_user.id}"), types.InlineKeyboardButton("❌ رد", callback_data=f"admin_reject_{call.from_user.id}"))
            bot.send_message(ADMIN_ID, f"📥 **درخواست جدید!**\n👤 کاربر: @{call.from_user.username}\n🌍 جبهه: {name}", reply_markup=admin_markup, parse_mode="Markdown")
    except Exception as e:
        print(f"Error in selection: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('mil_'))
def handle_military_click(call):
    country_code = call.data.replace('mil_', '')
    military_text = get_military_info(country_code)
    back_markup = types.InlineKeyboardMarkup()
    back_markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_mil_menu"))
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=military_text, reply_markup=back_markup, parse_mode="Markdown")
    except Exception:
        bot.send_message(call.message.chat.id, military_text, reply_markup=back_markup)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_mil_menu")
def back_to_military_hub(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="⚔️ **فاکشن مورد نظر خود را برای مانیتورینگ انتخاب کنید:**", reply_markup=get_military_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_decision(call):
    if call.from_user.id != ADMIN_ID: return
    action = call.data.replace("admin_", "")
    if action.startswith("approve_"):
        target_id = int(action.replace("approve_", ""))
        player = get_player(target_id)
        if player:
            approve_player(target_id)
            try: bot.send_message(target_id, f"🎉 **درخواست شما تایید شد!**")
            except: pass
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"✅ تایید شد.")
    elif action.startswith("reject_"):
        target_id = int(action.replace("reject_", ""))
        player = get_player(target_id)
        if player:
            reject_player(target_id)
            try: bot.send_message(target_id, f"❌ درخواست شما رد شد.")
            except: pass
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"❌ رد شد.")

# --- سرور فریب دادن رندر ---
class DummyWebhookServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Velora Bot is Live and Running!")

def run_web_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), DummyWebhookServer)
        print(f"🌍 Web Server Dummy started on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"❌ WEB SERVER ERROR: {e}")

if __name__ == '__main__':
    web_thread = threading.Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()
    
    print("🤖 Velora Game Bot Starting Polling...")
    try:
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print(f"❌ CRITICAL BOT POLLING ERROR: {e}")
    
