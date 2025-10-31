from flask import Flask
from threading import Thread
import logging

app = Flask('')

@app.route('/')
def home():
    return "🎤 Discord TTS Bot is running!"

@app.route('/status')
def status():
    return {
        "status": "online",
        "bot": "Discord TTS Bot",
        "message": "Bot is alive and running 24/7"
    }

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Start Flask server in background thread to keep Replit awake"""
    t = Thread(target=run)
    t.daemon = True
    t.start()
    logging.info("Keep-alive server started on port 8080")
