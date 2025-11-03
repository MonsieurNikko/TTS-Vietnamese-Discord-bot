# 🚀 Deploy Guide

## Quick Deploy

### Cybrance / Railway / Render
1. Fork repo
2. New Project → Import from GitHub
3. Add env: `Discord_Token=YOUR_TOKEN`
4. Deploy! (Dockerfile auto-detected)

### Docker (VPS)
```bash
docker build -t tts-bot .
docker run -d -e Discord_Token=YOUR_TOKEN --name tts-bot tts-bot
```

### Docker Compose (VPS)
```bash
git clone <repo-url>
cd TTS-Vietnamese-Discord-bot
echo "Discord_Token=YOUR_TOKEN" > .env
docker-compose up -d
```

## Requirements
- Python 3.11+
- FFmpeg (auto-installed in Docker)
- libopus (auto-installed in Docker)

## Verify Success
Check logs for:
```
✅ FFmpeg found
✅ Opus loaded
✅ Bot connected successfully!
```

## 📖 Cách sử dụng Bot

### 1. Vào voice channel
- Join vào bất kỳ voice channel nào trong server

### 2. Sử dụng lệnh TTS
**Tiếng Việt (mặc định):**
```
!tts xin chào mọi người
!nói hôm nay trời đẹp
```

**Tiếng khác - thêm mã ngôn ngữ:**
```
!tts en hello everyone        → Tiếng Anh
!tts ja こんにちは            → Tiếng Nhật
!tts ko 안녕하세요             → Tiếng Hàn
!tts fr bonjour               → Tiếng Pháp
!tts de guten tag             → Tiếng Đức
!tts es hola amigos           → Tiếng Tây Ban Nha
!tts zh 你好世界               → Tiếng Trung
```

**Mã ngôn ngữ hỗ trợ:**
- `vi` = Tiếng Việt (Vietnamese)
- `en` = Tiếng Anh (English)
- `ja` = Tiếng Nhật (Japanese - 日本語)
- `ko` = Tiếng Hàn (Korean - 한국어)
- `fr` = Tiếng Pháp (French - Français)
- `de` = Tiếng Đức (German - Deutsch)
- `es` = Tiếng Tây Ban Nha (Spanish - Español)
- `zh` = Tiếng Trung (Chinese - 中文)

### 3. Quản lý TTS queue
```
!skip      → Bỏ qua TTS đang phát
!queue     → Xem danh sách TTS chờ
!clear     → Xóa toàn bộ queue
!leave     → Bot rời voice channel
```

## Troubleshooting

**Bot not connecting?**
- Verify `Discord_Token` in environment variables
- Enable Message Content Intent in Discord Developer Portal

**FFmpeg/Opus errors?**
- Use Dockerfile (recommended)
- Platform must support Docker builds

## Commands
```bash
docker logs -f tts-bot          # View logs
docker restart tts-bot          # Restart
docker-compose restart          # Restart (compose)
docker-compose down             # Stop
```

---

**Deploy takes ~2 minutes. Bot runs 24/7 automatically! 🎉**
