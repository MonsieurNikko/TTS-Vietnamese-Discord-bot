# 🎤 Discord TTS Bot

Text-to-Speech bot tiếng Việt chất lượng cao, hỗ trợ 8 ngôn ngữ.

## ✨ Features
- 🗣️ TTS tiếng Việt (gTTS)
- 🌐 8 ngôn ngữ: vi, en, ja, ko, fr, de, es, zh
- 📝 Queue system
- 🚪 Auto-disconnect
- 🔔 Multi-server

## 🎮 Commands

### Lệnh TTS cơ bản
```bash
!tts <text>              # Đọc tiếng Việt (mặc định)
!nói <text>              # Alias của !tts
```

**Ví dụ:**
- `!tts xin chào các bạn` → Đọc bằng tiếng Việt
- `!nói tôi là bot Discord` → Đọc bằng tiếng Việt

### TTS với ngôn ngữ khác
```bash
!tts <mã_ngôn_ngữ> <text>    # Đọc bằng ngôn ngữ chỉ định
```

**Danh sách ngôn ngữ hỗ trợ:**
| Mã   | Ngôn ngữ | Ví dụ |
|------|----------|-------|
| `vi` | Tiếng Việt | `!tts vi xin chào` |
| `en` | English (Tiếng Anh) | `!tts en hello world` |
| `ja` | 日本語 (Tiếng Nhật) | `!tts ja こんにちは` |
| `ko` | 한국어 (Tiếng Hàn) | `!tts ko 안녕하세요` |
| `fr` | Français (Tiếng Pháp) | `!tts fr bonjour` |
| `de` | Deutsch (Tiếng Đức) | `!tts de guten tag` |
| `es` | Español (Tiếng Tây Ban Nha) | `!tts es hola` |
| `zh` | 中文 (Tiếng Trung) | `!tts zh 你好` |

**Lưu ý:** Nếu không chỉ định mã ngôn ngữ, bot sẽ tự động đọc bằng tiếng Việt.

### Lệnh quản lý queue
```bash
!skip           # Bỏ qua bài đang phát hiện tại
!queue          # Xem danh sách TTS đang chờ
!clear          # Xóa toàn bộ queue
!leave          # Bot rời khỏi voice channel
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
