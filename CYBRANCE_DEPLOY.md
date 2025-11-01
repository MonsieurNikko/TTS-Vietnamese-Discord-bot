# 🚀 Deploy trên Cybrance

## Yêu cầu
- Tài khoản Cybrance
- Discord Bot Token

## Bước 1: Chuẩn bị

### Push code lên GitHub (nếu chưa)
```bash
git add .
git commit -m "Ready for Cybrance deployment"
git push
```

## Bước 2: Deploy trên Cybrance

### Option 1: Deploy từ GitHub

1. Đăng nhập vào [Cybrance](https://cybrance.com)
2. Tạo **New Project**
3. Chọn **Import from GitHub**
4. Chọn repository: `TTS-Vietnamese-Discord-bot`
5. Cybrance tự động detect `Dockerfile`

### Option 2: Deploy bằng Docker Compose

1. Upload project lên Cybrance server
2. Tạo file `.env` với nội dung:
   ```
   Discord_Token=YOUR_BOT_TOKEN_HERE
   ```
3. Chạy lệnh:
   ```bash
   docker-compose up -d
   ```

## Bước 3: Cấu hình Environment Variables

Trên Cybrance Dashboard:
1. Vào **Settings** → **Environment Variables**
2. Thêm biến:
   - Key: `Discord_Token`
   - Value: `YOUR_DISCORD_BOT_TOKEN`

## Bước 4: Build & Deploy

Cybrance sẽ tự động:
1. Build Docker image từ `Dockerfile`
2. Install ffmpeg và libopus
3. Install Python dependencies
4. Start bot

## Xác nhận Deploy thành công

Check logs trên Cybrance, bạn sẽ thấy:
```
✅ FFmpeg found
✅ Opus loaded: libopus.so.0
✅ Loa phát thanh#2319 đã kết nối thành công!
✅ Bot đang hoạt động trên 2 server(s)
```

## Troubleshooting

### Bot không kết nối
- Kiểm tra `Discord_Token` trong Environment Variables
- Verify bot có Message Content Intent enabled

### Lỗi FFmpeg/Opus
- Đảm bảo `Dockerfile` được sử dụng (không phải buildpack)
- Check logs: `docker logs discord-tts-bot`

## Commands

### Xem logs
```bash
docker logs -f discord-tts-bot
```

### Restart bot
```bash
docker-compose restart
```

### Stop bot
```bash
docker-compose down
```

## 🎉 Bot đã chạy!

Test trong Discord:
```
tts xin chào
tts en hello world
```

---

**Lưu ý:** Cybrance tự động restart bot khi crash (restart: unless-stopped)
