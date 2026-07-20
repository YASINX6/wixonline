import telebot
from telebot import types
import psycopg2
import sys
import os
import threading
import importlib
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime  # اضافه شدن کتابخانه زمان برای رسید ادمین

# پیدا کردن مسیر دقیق پوشه جاری ربات در هاست رندر
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# اضافه کردن مسیر پوشه data به سیستم جهت امپورت صحیح
DATA_DIR = os.path.join(BASE_DIR, "data")
if DATA_DIR not in sys.path:
    sys.path.append(DATA_DIR)

print("🔄 Starting Velora Game Bot with Cloud Neon Database...")

# لینک دیتابیس ابری دائمی شما
DB_URL = "postgresql://neondb_owner:npg_jnRUSfz04bNT@ep-lucky-union-avtudu6k.c-11.us-east-1.aws.neon.tech/neondb?sslmode=require"

# فراخوانی اطلاعات نظامی از پوشه data
def get_military_info(country_code):
    try:
        target_path = os.path.join(DATA_DIR, "military_data.py")
        if os.path.exists(target_path):
            import military_data
            importlib.reload(military_data)
            if hasattr(military_data, "get_military_info"):
                return military_data.get_military_info(country_code)
            else:
                return "❌ خطا: تابع get_military_info در فایل military_data.py تعریف نشده است."
        else:
            return f"❌ خطا: فایل داده‌های نظامی در مسیر {target_path} یافت نشد."
    except Exception as e:
        return f"⚠️ خطا در خواندن اطلاعات نظامی از فایل: {e}"

API_TOKEN = '8648815822:AAEMeDbHCd3a_D_SQCTnLlT-mES5irfpyBo'
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 7961155790
ADMIN_USERNAME = "EXLUG" 

def init_db():
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                role TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Cloud Database initialized successfully.")
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")

init_db()

def get_player(user_id):
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players WHERE user_id = %s", (user_id,))
        player = cursor.fetchone()
        cursor.close()
        conn.close()
        return player
    except:
        return None

def is_faction_taken(faction_name):
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM players WHERE role = %s AND (status = 'approved' OR status = 'pending')", (faction_name,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except:
        return False

def set_pending_player(user_id, username, role):
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO players (user_id, username, role, status)
            VALUES (%s, %s, %s, 'pending')
            ON CONFLICT (user_id) 
            DO UPDATE SET username = EXCLUDED.username, role = EXCLUDED.role, status = EXCLUDED.status
        ''', (user_id, username, role))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ DB INSERT ERROR: {e}")

def approve_player(user_id):
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("UPDATE players SET status = 'approved' WHERE user_id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except:
        pass

def ban_player(user_id):
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO players (user_id, username, role, status)
            VALUES (%s, 'BANNED', 'None', 'banned')
            ON CONFLICT (user_id) 
            DO UPDATE SET username = 'BANNED', role = 'None', status = 'banned'
        ''', (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except:
        return False

def unban_player(user_id):
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM players WHERE user_id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except:
        return False

def reject_player(user_id):
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM players WHERE user_id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except:
        pass

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

def is_banned(user_id):
    player = get_player(user_id)
    if player and player[3] == 'banned':
        return True
    return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if is_banned(message.from_user.id): return
    player = get_player(message.from_user.id)
    
    if player and player[3] == 'approved':
        faction_name = player[2]
        entity_code = "unknown"
        
        for cat, entities in GAME_ENTITIES.items():
            for code, info in entities.items():
                if code in faction_name.lower() or info["name"] in faction_name:
                    entity_code = code
                    break

        welcome_approved = f"⚔️ **فرمانده به ستاد فرماندهی خوش آمدید!**\n🎭 جبهه تحت کنترل شما: **{faction_name}**\n\n👇 جهت مانیتورینگ فاکشن خود از دکمه‌های زیر استفاده کنید:"
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📊 لیست اقتصادی", callback_data="eco_locked"),
            types.InlineKeyboardButton("🪖 لیست نظامی", callback_data=f"user_mil_{entity_code}")
        )
        bot.send_message(message.chat.id, welcome_approved, reply_markup=markup, parse_mode="Markdown")
        return
        
    elif player and player[3] == 'pending':
        bot.send_message(message.chat.id, f"⏳ **درخواست قبلی شما برای جبهه ({player[2]}) در انتظار تایید است.**")
        return

    welcome_text = "🌍 **به بزرگترین شبیه‌ساز جنگ جهانی سوم خوش آمدید!**\n👇 جبهه خود را انتخاب کنید:"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🌍 رزرو کشور یا گروهک", callback_data="main_menu"))
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def main_menu(call):
    if is_banned(call.from_user.id): return
    
    player = get_player(call.from_user.id)
    if player and player[3] in ['approved', 'pending']:
        bot.answer_callback_query(call.id, f"❌ شما از قبل جبهه ({player[2]}) را دارید!", show_alert=True)
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🏛️ اروپا و آمریکا", callback_data="cat_europe"),
        types.InlineKeyboardButton("🌏 آسیا", callback_data="cat_asia"),
        types.InlineKeyboardButton("🌍 آفریقا", callback_data="cat_africa"),
        types.InlineKeyboardButton("🪖 گروهک‌ها", callback_data="cat_groups")
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🚩 **منطقه خود را انتخاب کنید:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def show_category(call):
    if is_banned(call.from_user.id): return
    category_code = call.data.replace("cat_", "")
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for code, info in GAME_ENTITIES[category_code].items():
        btn_text = f"⭐ {info['name']} (VIP)" if info["vip"] else info["name"]
        buttons.append(types.InlineKeyboardButton(btn_text, callback_data=f"select_{category_code}_{code}"))
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="👇 **لیست جبهه‌های موجود:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("select_"))
def process_selection(call):
    if is_banned(call.from_user.id): return
    try:
        parts = call.data.split("_", 2)
        category, entity_code = parts[1], parts[2]
        entity_info = GAME_ENTITIES[category][entity_code]
        name = entity_info["name"]
        role_name = f"{name} (VIP)" if entity_info["vip"] else name
        
        current_player = get_player(call.from_user.id)
        if current_player and current_player[3] in ['approved', 'pending']:
            bot.answer_callback_query(call.id, f"❌ شما از قبل جبهه ({current_player[2]}) را رزرو کرده‌اید!", show_alert=True)
            return

        if is_faction_taken(role_name):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 بازگشت به لیست", callback_data=f"cat_{category}"))
            bot.edit_message_text(
                chat_id=call.message.chat.id, 
                message_id=call.message.message_id, 
                text=f"❌ **فرمانده، جبهه {name} از قبل توسط بازیکن دیگری رزرو یا مدیریت می‌شود!**\n\nلطفاً کشور یا جبهه دیگری را انتخاب کنید.", 
                reply_markup=markup, 
                parse_mode="Markdown"
            )
            return
        
        if entity_info["vip"]:
            set_pending_player(call.from_user.id, call.from_user.username or "ندارد", role_name)
            text = f"💎 **درخواست رزرو جبهه ویژه (VIP): {name}**\n\n💰 **هزینه رزرو ویژه:** {entity_info['price']}\n\n⚠️ درخواست ثبت شد. جهت پرداخت به مالک پیام دهید:"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("💬 پیام به مالک", url=f"https://t.me/{ADMIN_USERNAME}"), types.InlineKeyboardButton("🔙 بازگشت", callback_data=f"cat_{category}"))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")
            
            admin_markup = types.InlineKeyboardMarkup()
            admin_markup.add(types.InlineKeyboardButton("✅ تایید VIP", callback_data=f"adm_app_{call.from_user.id}"), types.InlineKeyboardButton("❌ رد", callback_data=f"adm_rej_{call.from_user.id}"))
            bot.send_message(ADMIN_ID, f"👑 **درخواست جبهه VIP!**\n👤 کاربر: @{call.from_user.username}\n🆔 آیدی: `{call.from_user.id}`\n👑 فاکشن: {name}", reply_markup=admin_markup, parse_mode="Markdown")
        else:
            set_pending_player(call.from_user.id, call.from_user.username or "ندارد", role_name)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 بازگشت به منو", callback_data="main_menu"))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"⏳ **درخواست رزرو جبهه {name} ثبت شد و برای ادمین ارسال گردید.**", reply_markup=markup, parse_mode="Markdown")
            
            admin_markup = types.InlineKeyboardMarkup()
            admin_markup.add(types.InlineKeyboardButton("✅ تایید", callback_data=f"adm_app_{call.from_user.id}"), types.InlineKeyboardButton("❌ رد", callback_data=f"adm_rej_{call.from_user.id}"))
            bot.send_message(ADMIN_ID, f"📥 **درخواست جدید جبهه معمولی!**\n👤 کاربر: @{call.from_user.username}\n🆔 آیدی: `{call.from_user.id}`\n🌍 جبهه: {name}", reply_markup=admin_markup, parse_mode="Markdown")
    except Exception as e:
        print(f"Error in selection: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "eco_locked")
def handle_eco_locked(call):
    bot.answer_callback_query(call.id, "🔒 این بخش در آپدیت‌های آینده فعال می‌شود!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("user_mil_"))
def handle_user_military(call):
    if is_banned(call.from_user.id): return
    entity_code = call.data.replace("user_mil_", "")
    
    military_text = get_military_info(entity_code)
    
    back_markup = types.InlineKeyboardMarkup()
    back_markup.add(types.InlineKeyboardButton("🔙 بازگشت به ستاد فرماندهی", callback_data="back_to_user_menu"))
    
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=military_text, reply_markup=back_markup, parse_mode="Markdown")
    except:
        bot.send_message(call.message.chat.id, military_text, reply_markup=back_markup)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_user_menu")
def back_to_user_menu(call):
    if is_banned(call.from_user.id): return
    player = get_player(call.from_user.id)
    if player:
        faction_name = player[2]
        entity_code = "unknown"
        for cat, entities in GAME_ENTITIES.items():
            for code, info in entities.items():
                if code in faction_name.lower() or info["name"] in faction_name:
                    entity_code = code
                    break
                    
        welcome_approved = f"⚔️ **فرمانده به ستاد فرماندهی خوش آمدید!**\n🎭 جبهه تحت کنترل شما: **{faction_name}**\n\n👇 جهت مانیتورینگ فاکشن خود از دکمه‌های زیر استفاده کنید:"
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📊 لیست اقتصادی", callback_data="eco_locked"),
            types.InlineKeyboardButton("🪖 لیست نظامی", callback_data=f"user_mil_{entity_code}")
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=welcome_approved, reply_markup=markup, parse_mode="Markdown")

# 🛠️ بخش بازنویسی‌شده دسیژن ادمین همراه با تولید رسید دیجیتال و مشخصات کامل کاربر
@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def admin_decision(call):
    if call.from_user.id != ADMIN_ID: return
    action = call.data.replace("adm_", "")
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    if action.startswith("app_"):
        target_id = int(action.replace("app_", ""))
        player = get_player(target_id)
        if player:
            approve_player(target_id)
            try: 
                bot.send_message(target_id, f"🎉 **درخواست شما برای جبهه {player[2]} تایید شد!**\n\n👇 همین حالا دستور /start را بفرستید تا وارد ستاد فرماندهی خود شوید!", parse_mode="Markdown")
            except: 
                pass
            
            # فرمت کردن آیدی تلگرام بازیکن جهت تگ شدن صحیح
            user_mention = f"@{player[1]}" if player[1] != "ندارد" else "ندارد"
            
            receipt_text = (
                f"✅ **کشور با موفقیت تایید و واگذار شد**\n\n"
                f"🏰 **نام جبهه/کشور:** {player[2]}\n"
                f"👤 **مالک جبهه:** {user_mention}\n"
                f"🆔 **آیدی عددی مالک:** `{player[0]}`\n"
                f"⏰ **زمان تایید نهایی:** {current_time}"
            )
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=receipt_text, parse_mode="Markdown")
            
    elif action.startswith("rej_"):
        target_id = int(action.replace("rej_", ""))
        player = get_player(target_id)
        if player:
            reject_player(target_id)
            try: 
                bot.send_message(target_id, f"❌ درخواست شما رد شد.")
            except: 
                pass
            
            user_mention = f"@{player[1]}" if player[1] != "ندارد" else "ندارد"
            
            receipt_text = (
                f"❌ **درخواست رزرو جبهه رد شد**\n\n"
                f"🏰 **نام جبهه/کشور:** {player[2]}\n"
                f"👤 **متقاضی:** {user_mention}\n"
                f"🆔 **آیدی عددی متقاضی:** `{player[0]}`\n"
                f"⏰ **زمان رد درخواست:** {current_time}"
            )
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=receipt_text, parse_mode="Markdown")

class DummyWebhookServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Velora Bot is Live!")

def run_web_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), DummyWebhookServer)
        server.serve_forever()
    except:
        pass

if __name__ == '__main__':
    web_thread = threading.Thread(target=run_web_server)
    web_thread.daemon =
