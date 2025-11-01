# 🎤 Discord TTS Bot

Text-to-Speech bot tiếng Việt chất lượng cao, hỗ trợ 8 ngôn ngữ.

## ✨ Features
- 🗣️ TTS tiếng Việt (gTTS)
- 🌐 8 ngôn ngữ: vi, en, ja, ko, fr, de, es, zh
- 📝 Queue system
- 🚪 Auto-disconnect
- 🔔 Multi-server

## 🎮 Commands
```
tts <text>      # TTS
tts en hello    # English
skip            # Skip
queue           # View queue
clear           # Clear queue
leave           # Disconnect
```

## 🚀 Deploy

### Cybrance / Railway / Render
1. Fork repo
2. New Project → From GitHub
3. Add: `Discord_Token=YOUR_TOKEN`
4. Deploy!

👉 [Deploy Guide](./DEPLOY.md)

## 💻 Local
```bash
pip install -r requirements.txt
echo "Discord_Token=YOUR_TOKEN" > .env
python tts_bot.py
```

## 📋 Files
- `tts_bot.py` - Main code
- `Dockerfile` - Container config
- `docker-compose.yml` - Compose config
- `requirements.txt` - Dependencies

## 📝 License
MIT
