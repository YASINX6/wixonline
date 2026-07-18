import json
import os

# نام فایلی که اطلاعات بازیکنا توش ذخیره میشه
PLAYERS_FILE = "players.json"

def load_players():
    """خواندن لیست بازیکنان از فایل JSON"""
    if not os.path.exists(PLAYERS_FILE):
        return {}
    try:
        with open(PLAYERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_players(players_data):
    """ذخیره لیست بازیکنان در فایل JSON"""
    with open(PLAYERS_FILE, "w", encoding="utf-8") as f:
        json.dump(players_data, f, ensure_ascii=False, indent=4)

def get_player_faction(user_id):
    """گرفتن نام فاکشن بازیکن"""
    players = load_players()
    user_key = str(user_id)
    
    if user_key in players:
        return players[user_key]["faction"]
    return None

def register_player(user_id, faction_name):
    """ثبت اولیه بازیکن و کشوری که انتخاب کرده"""
    players = load_players()
    user_key = str(user_id)
    
    players[user_key] = {
        "faction": faction_name.lower().strip(),
        "status": "pending"
    }
    save_players(players)
      
