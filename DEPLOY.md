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
