# 🚀 Hướng dẫn Deploy

## Railway (Khuyến nghị) ⭐

### Bước 1: Chuẩn bị
```bash
git add .
git commit -m "Ready for Railway"
git push
```

### Bước 2: Deploy
1. Truy cập [Railway.app](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Chọn repo này
4. Railway tự động detect và build

### Bước 3: Config
1. Vào **Variables** tab
2. Thêm: `Discord_Token` = `YOUR_BOT_TOKEN`
3. Save và redeploy

### Kết quả
✅ Railway tự động cài: Python, FFmpeg, libopus  
✅ Bot chạy 24/7 miễn phí (500h/tháng)  
✅ Auto-restart khi crash

---

## Render

### Deploy
1. Tạo **New Web Service**
2. Connect repo
3. Settings:
   - **Environment**: Docker
   - **Docker Command**: `python tts_bot.py`
4. Thêm env var: `Discord_Token`

---

## Heroku

### Deploy
```bash
heroku create your-bot-name
heroku config:set Discord_Token=YOUR_TOKEN
git push heroku main
```

File `Procfile` đã sẵn sàng.

---

## DigitalOcean / VPS

### Docker
```bash
# Clone repo
git clone <repo-url>
cd TTS-Vietnamese-Discord-bot

# Build & Run
docker build -t tts-bot .
docker run -d \
  -e Discord_Token=YOUR_TOKEN \
  --name tts-bot \
  --restart unless-stopped \
  tts-bot
```

### Manual
```bash
# Install dependencies
apt-get update
apt-get install -y python3 python3-pip ffmpeg libopus0

# Install Python packages
pip3 install -r requirements.txt

# Run with systemd
sudo nano /etc/systemd/system/tts-bot.service
```

Content:
```ini
[Unit]
Description=Discord TTS Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/TTS-Vietnamese-Discord-bot
Environment="Discord_Token=YOUR_TOKEN"
ExecStart=/usr/bin/python3 tts_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable tts-bot
sudo systemctl start tts-bot
```

---

## Troubleshooting

### Railway: "No start command"
✅ **Đã fix:** File `railway.json` và `nixpacks.toml` đã có.  
→ Chỉ cần redeploy.

### Opus/FFmpeg errors
✅ **Đã fix:** `nixpacks.toml` tự động cài.  
→ Đảm bảo Railway dùng file này.

### Bot không online
1. Check logs trên Railway
2. Verify `Discord_Token` đúng
3. Check bot có permissions trong Discord Developer Portal

---

## So sánh Platforms

| Platform | Free Tier | Setup | Auto-deploy | Recommend |
|----------|-----------|-------|-------------|-----------|
| **Railway** | 500h/month | ⭐⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐⭐ |
| Render | 750h/month | ⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐ |
| Heroku | Limited | ⭐⭐⭐ | ✅ | ⭐⭐⭐ |
| VPS | Paid | ⭐⭐ | ❌ | ⭐⭐⭐⭐ |

**Khuyến nghị: Railway** - Dễ nhất, tự động nhất, miễn phí tốt nhất!
