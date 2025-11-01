# ⚡ Quick Start - 5 phút Deploy!

## 1️⃣ Fork Repo này

## 2️⃣ Deploy trên Railway
1. Vào [Railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub**
3. Chọn repo vừa fork
4. Đợi deploy xong (~2 phút)

## 3️⃣ Config Bot Token
1. Click vào project
2. **Variables** tab
3. Add: `Discord_Token` = `YOUR_BOT_TOKEN`
4. Save (auto redeploy)

## 4️⃣ Xong! 🎉

Bot đã online và chạy 24/7!

---

## Lấy Bot Token

1. [Discord Developer Portal](https://discord.com/developers/applications)
2. Tạo Application mới
3. **Bot** tab → **Reset Token** → Copy
4. **Bot** tab → Enable: 
   - Message Content Intent
   - Server Members Intent
5. **OAuth2** → **URL Generator**:
   - Scopes: `bot`
   - Permissions: `Connect`, `Speak`, `Send Messages`
6. Copy link và invite bot vào server

---

## Test Bot

Vào Discord:
```
tts xin chào
tts en hello world
```

Done! 🚀
