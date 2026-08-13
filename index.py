from flask import Flask

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "✅ Bot is working!"

@app.route('/test', methods=['GET'])
def test():
    return "✅ Test route works!"

if __name__ == '__main__':
    app.run(debug=False)
