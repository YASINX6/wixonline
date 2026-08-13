from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# اول ببینیم Environment Variables درست تنظیم شدن
print("🔍 Checking environment variables...")
print(f"TELEGRAM_BOT_TOKEN: {'✅ Set' if os.getenv('TELEGRAM_BOT_TOKEN') else '❌ Not set'}")
print(f"DATABASE_URL: {'✅ Set' if os.getenv('DATABASE_URL') else '❌ Not set'}")
print(f"ADMIN_ID: {os.getenv('ADMIN_ID', 'Not set')}")

@app.route('/', methods=['GET'])
def home():
    return "✅ Bot server is running! Webhook is active."

@app.route(f'/{os.getenv("TELEGRAM_BOT_TOKEN", "test")}', methods=['POST'])
def webhook():
    return jsonify({"status": "ok"}), 200

@app.route('/debug', methods=['GET'])
def debug():
    """این صفحه نشون میده که متغیرها درستن یا نه"""
    return f"""
    <h2>Debug Info:</h2>
    <ul>
        <li>TELEGRAM_BOT_TOKEN: {'✅' if os.getenv('TELEGRAM_BOT_TOKEN') else '❌'}</li>
        <li>DATABASE_URL: {'✅' if os.getenv('DATABASE_URL') else '❌'}</li>
        <li>ADMIN_ID: {os.getenv('ADMIN_ID', '')}</li>
    </ul>
    """

if __name__ == '__main__':
    app.run(debug=False)
