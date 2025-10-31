# 🎤 Discord TTS Bot - Tiếng Việt

Bot Discord Text-to-Speech đơn giản, ổn định, có thể chạy 24/7 miễn phí.

## ✨ Tính năng

- 🗣️ **TTS tiếng Việt** chất lượng cao (gTTS)
- � **Không đọc tên người dùng**: tên chỉ hiển thị trong chat (embed), bot chỉ đọc nội dung
- 🚪 **Auto-disconnect**: tự rời khi không còn ai trong voice và sau **1 phút** không hoạt động
- 🌐 **Multi-server**: hoạt động trên nhiều server cùng lúc
- 📝 **Queue system**: xử lý tuần tự, tránh lag
- 🛡️ **Error handling**: an toàn, không crash
- 🔔 **Thông báo bận**: nếu bot đang ở room khác, sẽ báo “Tôi đang hoạt động ở <room>”

## 🎮 Sử dụng

```
tts xin chào         # Đọc văn bản (chỉ đọc nội dung)
skip                 # Bỏ qua TTS hiện tại
queue                # Xem hàng đợi
clear                # Xóa hàng đợi
leave                # Bot rời channel
huongdan             # Trợ giúp
```

---

## 💻 Chạy Local (Windows)

### 1. Cài đặt
```powershell
# Tạo môi trường ảo
python -m venv venv
.\venv\Scripts\Activate.ps1

# Cài packages
pip install -r requirements.txt

# Cài FFmpeg
winget install --id=Gyan.FFmpeg -e
```

### 2. Setup
Tạo file `.env`:
```
Discord_Token=YOUR_TOKEN_HERE
```

### 3. Chạy
```powershell
.\venv\Scripts\Activate.ps1
python tts_bot.py
```

**Lưu ý:** Mở PowerShell MỚI sau khi cài FFmpeg!

---

## ☁️ Deploy 24/7 Miễn Phí (Replit)

### Quick Start:
1. Vào https://replit.com → Tạo Python Repl
2. Upload: `tts_bot.py`, `keep_alive.py`, `requirements.txt`, `.replit`, `replit.nix`
3. Secrets (🔒): Thêm `Discord_Token`
4. Click Run ▶️
5. Setup UptimeRobot.com với URL Replit (ping mỗi 5 phút)

**→ Bot chạy 24/7 miễn phí!**

📖 **Chi tiết:** Xem `REPLIT_DEPLOY.md`

---

## ⚙️ Cấu hình nhanh

Các thiết lập chính nằm đầu file `tts_bot.py` (class `Config`):

```python
PREFIX = ''                    # Không cần prefix
TIMEOUT_MINUTES = 1            # Auto-disconnect sau 1 phút không hoạt động
MAX_TEXT_LENGTH = 200          # Độ dài văn bản tối đa
ANNOUNCE_USERNAME = False      # Không đọc tên người dùng
```

---

## 📁 Files Quan Trọng

```
TTSbot/
├── tts_bot.py          # Bot chính ⭐
├── keep_alive.py       # Web server (Replit)
├── requirements.txt    # Dependencies
├── .env                # Token (tạo thủ công)
├── .replit            # Config Replit
├── replit.nix         # FFmpeg (Replit)
└── README.md          # File này
```

---

## 🔧 Xử Lý Lỗi

| Lỗi | Giải pháp |
|-----|-----------|
| **Không kết nối Discord** | Check `Discord_Token` trong `.env` |
| **Không có âm thanh** | Cài FFmpeg, mở PowerShell MỚI |
| **Import error** | `pip install -r requirements.txt` |
| **Bot lag/crash** | Restart bot, check internet |
| **Bot báo bận** | Bot đang ở room khác: gõ `leave` tại room đó hoặc đợi 1 phút |

---

## 💡 Tips

- Bot join nhiều server khác nhau được
- Mỗi server có queue riêng
- Văn bản max 200 ký tự (đổi trong config)

---

## 🆘 Support

1. Đọc phần **Xử Lý Lỗi**
2. Check logs trong Console
3. Test FFmpeg: `ffmpeg -version`
4. Reinstall: `pip install -r requirements.txt`

---

## 📄 License

MIT - Sử dụng tự do

---

**Simple. Powerful. Free 24/7. Enjoy! 🎉**
