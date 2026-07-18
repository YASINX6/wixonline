import telebot
from telebot import types
import sqlite3
import sys
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# پیدا کردن مسیر دقیق پوشه جاری ربات
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("🔄 Starting Velora Game Bot with Raw Loader...")

# خواندن مستقیم دیتای نظامی از فایل به صورت متنی (بدون نیاز به امپورت)
def get_military_info(country_code):
    file_path = os.path.join(BASE_DIR, "military_data.py")
    
    if not os.path.exists(file_path):
        return f"❌ خطا: فایل military_data.py در مسیر {file_path} فیزیکی سرور یافت نشد."
        
    try:
        # باز کردن و خواندن فایل با رمزگذاری UTF-8 برای پشتیبانی از فارسی
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # پیدا کردن متن فاکشن مورد نظر در فایل
        # این بخش دنبال کد کشور در دیتابیس متنی می‌گردد
        lines = content.split('\n')
        extracted_text = []
        capture = False
        
        for line in lines:
            if f'"{country_code}":' in line or f"'{country_code}':" in line:
                capture = True
                # برداشتن متن داخل کوتیشن
                start_idx = line.find('"') if '"' in line else line.find("'")
                # اگر متن در همان خط اول کلید بود
                if start_idx != -1:
                    line_data = line[start_idx:].strip().strip(',').strip('"').strip("'")
                    if line_data and not line_data.startswith(country_code):
                        extracted_text.append(line_data)
                continue
                
            if capture:
                if '"' in line or "'" in line:
                    clean_line = line.replace('\\n', '\n').strip().strip(',').strip('"').strip("'")
                    if clean_line.endswith('}'): # پایان دیکشنری
                        clean_line = clean_line.rstrip('}').strip().strip('"').strip("'")
                        if clean_line: extracted_text.append(clean_line)
                        break
                    extracted_text.append(clean_line)
                if line.strip().endswith(',') and not ('"' in line or "'" in line):
                    continue
                if '}' in line and not ('"' in line or "'" in line):
                    break
                    
        if extracted_text:
            # تبدیل کاراکترهای ترخیص خط به خط واقعی
            final_text = "\n".join(extracted_text).replace('\\n', '\n')
            return final_text
        else:
            return f"🪖 **اطلاعات نظامی این فاکشن به زودی آپدیت می‌شود.**\nکد سیستم: {country_code}"
            
    except Exception as e:
        return f"⚠️ خطا در خواندن متنی فایل نظامی: {e}"

API_TOKEN = '8648815822:AAEMeDbHCd3a_D_SQCTnLlT-mES5irfpyBo'
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 7961155790
ADMIN_USERNAME = "EXLUG" 

def init_db():
    try:
        conn = sqlite3.connect(os.path.join(BASE_DIR, 'wixonline.db'), timeout=10)
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
        print("✅ Database initialized.")
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")

init_db()

def get_player(user_id):
    try:
        conn = sqlite3.connect(os.path.join(BASE_DIR, 'wixonline.db'), timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
        player = cursor.fetchone()
        conn.close()
        return player
    except:
        return None

def set_pending_player(user_id, username, role):
    try:
        conn = sqlite3.connect(os.path.join(BASE_DIR, 'wixonline.db'), timeout=10)
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
        conn = sqlite3.connect(os.path.join(BASE_DIR, 'wixonline.db'), timeout=10)
        cursor = conn.cursor()
        cursor.execute("UPDATE players SET status = 'approved' WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    except:
        pass

def ban_player(user_id):
    try:
        conn = sqlite3.connect(os.path.join(BASE_DIR, 'wixonline.db'), timeout=10)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO players (user_id, username, role, status)
            VALUES (?, 'BANNED', 'None', 'banned')
        ''', (user_id,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def unban_player(user_id):
    try:
        conn = sqlite3.connect(os.path.join(BASE_DIR, 'wixonline.db'), timeout=10)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM players WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def reject_player(user_id):
    try:
        conn = sqlite3.connect(os.path.join(BASE_DIR, 'wixonline.db'), timeout=10)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM players WHERE user_id = ?", (user_id,))
        conn.commit()
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
        
        if entity_info["vip"]:
            set_pending_player(call.from_user.id, call.from_user.username or "ندارد", f"{name} (VIP)")
            text = f"💎 **درخواست رزرو جبهه ویژه (VIP): {name}**\n\n💰 **هزینه رزرو ویژه:** {entity_info['price']}\n\n⚠️ درخواست ثبت شد. جهت پرداخت به مالک پیام دهید:"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("💬 پیام به مالک", url=f"https://t.me/{ADMIN_USERNAME}"), types.InlineKeyboardButton("🔙 بازگشت", callback_data=f"cat_{category}"))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")
            
            admin_markup = types.InlineKeyboardMarkup()
            admin_markup.add(types.InlineKeyboardButton("✅ تایید VIP", callback_data=f"adm_app_{call.from_user.id}"), types.InlineKeyboardButton("❌ رد", callback_data=f"adm_rej_{call.from_user.id}"))
            bot.send_message(ADMIN_ID, f"👑 **درخواست جبهه VIP!**\n👤 کاربر: @{call.from_user.username}\n🆔 آیدی: `{call.from_user.id}`\n👑 فاکشن: {name}", reply_markup=admin_markup, parse_mode="Markdown")
        else:
            set_pending_player(call.from_user.id, call.from_user.username or "ندارد", name)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"⏳ **درخواست رزرو جبهه {name} ثبت شد.**")
            
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

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def admin_decision(call):
    if call.from_user.id != ADMIN_ID: return
    action = call.data.replace("adm_", "")
    if action.startswith("app_"):
        target_id = int(action.replace("app_", ""))
        player = get_player(target_id)
        if player:
            approve_player(target_id)
            try: bot.send_message(target_id, f"🎉 **درخواست شما برای جبهه {player[2]} تایید شد!**\n\n👇 همین حالا دستور /start را بفرستید تا وارد ستاد فرماندهی خود شوید!")
            except: pass
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"✅ جبهه کاربر ({player[2]}) تایید شد.")
    elif action.startswith("rej_"):
        target_id = int(action.replace("rej_", ""))
        player = get_player(target_id)
        if player:
            reject_player(target_id)
            try: bot.send_message(target_id, f"❌ درخواست شما رد شد.")
            except: pass
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"❌ درخواست کاربر رد شد.")

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
    web_thread.daemon = True
    web_thread.start()
    
    bot.infinity_polling(skip_pending=True)
    
