# 🚀 Deploy Bot lên Replit (24/7 Miễn Phí)

## 📋 Tóm tắt

Bot sẽ chạy **24/7 hoàn toàn miễn phí** trên Replit + UptimeRobot.

**Thời gian setup: 5 phút**

---

## 🎯 Bước 1: Tạo Replit

1. Vào https://replit.com
2. Đăng ký/Đăng nhập (miễn phí)
3. Click `+ Create Repl`
4. Chọn `Python` template
5. Đặt tên: `discord-tts-bot`

---

## 📤 Bước 2: Upload Files

Kéo thả các files sau vào Replit:

**Bắt buộc:**
- `tts_bot.py`
- `keep_alive.py`
- `requirements.txt`
- `.replit`
- `replit.nix`

**Tùy chọn:**
- `config.py`

---

## 🔐 Bước 3: Setup Token

1. Click biểu tượng 🔒 (Secrets) ở sidebar
2. Add new secret:
   - **Key:** `Discord_Token`
   - **Value:** Paste Discord bot token của bạn
3. Click `Add Secret`

---

## ▶️ Bước 4: Chạy Bot

1. Click nút `Run` ▶️ (màu xanh, giữa trên)
2. Replit tự động install packages
3. Chờ thấy:
   ```
   ✅ Keep-alive server started for Replit
   Loa phát thanh#2319 đã kết nối thành công!
   ```
4. Test trong Discord: `tts xin chào`

✅ **Bot đã chạy!** Nhưng sẽ sleep sau 1h nếu không ping.

---

## 🌐 Bước 5: Keep Bot Alive (UptimeRobot)

### 5.1. Lấy URL từ Replit
- Nhìn vào Webview (bên phải màn hình Replit)
- Copy URL, ví dụ: `https://discord-tts-bot.username.repl.co`

### 5.2. Setup UptimeRobot
1. Vào https://uptimerobot.com
2. Đăng ký (miễn phí)
3. Click `+ Add New Monitor`
4. Điền:
   - **Monitor Type:** `HTTP(s)`
   - **Friendly Name:** `Discord TTS Bot`
   - **URL:** Paste URL từ Replit
   - **Monitoring Interval:** `5 minutes`
5. Click `Create Monitor`

✅ **Xong!** UptimeRobot ping bot mỗi 5 phút → Bot không sleep.

---

## ✅ Kiểm Tra

### Bot chạy đúng nếu:
- ✅ Console: `đã kết nối thành công!`
- ✅ Webview: `🎤 Discord TTS Bot is running!`
- ✅ Bot online trong Discord
- ✅ Bot phản hồi `tts xin chào`
- ✅ UptimeRobot: `Up` (màu xanh)

---

## 🔧 Troubleshooting

### Bot không chạy?
```bash
pip install --force-reinstall -r requirements.txt
```
Click Run lại.

### FFmpeg not found?
- Stop bot (Ctrl+C)
- Check `replit.nix` có `pkgs.ffmpeg-full`
- Run lại

### Bot bị sleep?
- Check UptimeRobot active
- Verify URL ping đúng

---

## 💰 Chi Phí

**$0/tháng** - Hoàn toàn miễn phí!

| Dịch vụ | Plan | Giới hạn |
|---------|------|----------|
| Replit | Free | Unlimited projects |
| UptimeRobot | Free | 50 monitors |

---

## 🎯 Kết Quả

✅ Bot 24/7 miễn phí  
✅ FFmpeg hoạt động  
✅ Auto-restart  
✅ TTS tiếng Việt  

---

## 🔗 Links

- https://replit.com
- https://uptimerobot.com
- https://discord.com/developers

---

**Bot online 24/7! Test: `tts xin chào` 🎉**
