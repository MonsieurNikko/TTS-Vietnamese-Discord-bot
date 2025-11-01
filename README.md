# 🎤 Discord TTS Bot - Tiếng Việt

Bot Discord Text-to-Speech chất lượng cao, hỗ trợ đa ngôn ngữ.

## ✨ Tính năng

- 🗣️ TTS tiếng Việt chất lượng cao (gTTS)
- 🌐 Hỗ trợ 8 ngôn ngữ: vi, en, ja, ko, fr, de, es, zh
- 🚪 Auto-disconnect khi không hoạt động
- 📝 Queue system xử lý tuần tự
- 🔔 Multi-server support

## 🎮 Lệnh sử dụng

```bash
tts <text>      # Đọc văn bản
tts en hello    # Đọc tiếng Anh  
skip            # Bỏ qua
queue           # Xem hàng đợi
clear           # Xóa hàng đợi
leave           # Rời channel
```

## 🚀 Deploy nhanh

### Cybrance (Khuyến nghị) ⭐
1. Fork repo này
2. Tạo project mới trên [Cybrance](https://cybrance.com)
3. Import from GitHub
4. Thêm env var: `Discord_Token`
5. Deploy! (Dockerfile auto-detected)

👉 **Chi tiết:** [CYBRANCE_DEPLOY.md](./CYBRANCE_DEPLOY.md)

### Railway
1. New Project → From GitHub
2. Add env: `Discord_Token`
3. Auto deploy

### Render / Heroku
1. Upload code
2. Set environment: `Discord_Token`
3. Dockerfile auto-build

### Yêu cầu hệ thống
- Python 3.11+
- FFmpeg
- libopus

**Lưu ý:** `Dockerfile` và `nixpacks.toml` đã cấu hình sẵn tất cả dependencies.

## 💻 Chạy Local

```bash
# Clone & Install
git clone <repo-url>
cd TTS-Vietnamese-Discord-bot
pip install -r requirements.txt

# Cài FFmpeg (Windows)
winget install ffmpeg

# Setup
echo "Discord_Token=YOUR_TOKEN" > .env

# Run
python tts_bot.py
```

## 📁 Files quan trọng

- `tts_bot.py` - Main bot code  
- `Dockerfile` - Container config (ffmpeg + opus)
- `nixpacks.toml` - Railway config
- `railway.json` - Railway deploy settings
- `Procfile` - Heroku start command
- `requirements.txt` - Python dependencies

## ⚠️ Troubleshooting

### Railway: "No start command found"
→ File `railway.json` và `nixpacks.toml` đã sẵn sàng. Redeploy.

### Lỗi: `OpusNotLoaded`
→ Hosting thiếu libopus. Sử dụng `Dockerfile` hoặc `nixpacks.toml`.

### Lỗi: `FFmpeg not found`
→ Sử dụng `Dockerfile` hoặc `nixpacks.toml` để auto-install.

## 📝 License

MIT License - Free to use

---

**Deploy ngay trên Railway trong 5 phút! 🚀**
