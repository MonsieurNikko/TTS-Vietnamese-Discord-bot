# 🚀 Development & Release Workflow

**Mục tiêu:** Test an toàn trên PC, deploy lên Cybrance production không sợ crash.

---

## 📋 Tổng quan

| Environment | Chạy ở đâu | Bot Token | Discord Server | Mục đích |
|-------------|-----------|-----------|----------------|----------|
| **Development** | PC local | DEV Token | Server test riêng | Code & test tính năng |
| **Production** | Cybrance | PROD Token | Server chính | User thật sử dụng |

**Nguyên tắc vàng:**
- ✅ Luôn test trên DEV trước
- ❌ Không bao giờ code trực tiếp trên production
- ✅ Deploy production chỉ khi DEV đã test kỹ ≥30 phút

---

## 📁 Cấu trúc thư mục

```
TTS-Vietnamese-Discord-bot/
├── src/                      # Source code
│   └── tts_bot.py           # Bot chính (auto-detect environment)
├── config/                   # Configuration templates
│   ├── .env.dev.example     # Template cho DEV
│   └── .env.prod.example    # Template cho PROD
├── docs/                     # Documentation
│   ├── WORKFLOW.md          # File này - hướng dẫn toàn bộ
│   ├── README.md            # Mô tả project
│   └── DEPLOY.md            # Hướng dẫn deploy
├── venv/                     # Python virtual environment (Git-ignored)
├── .env.dev                  # DEV token (Git-ignored, tạo từ template)
├── .env.prod                 # PROD token backup (Git-ignored, optional)
├── .env                      # Production config (Git-ignored)
├── .gitignore               # Ignore sensitive files
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container config
├── docker-compose.yml       # Docker Compose config
└── README.md                # Main README (copy của docs/README.md)
```

**Lưu ý quan trọng:**
- ✅ Code chỉ có 1 file: `src/tts_bot.py` (dùng chung)
- ✅ Token khác nhau qua file `.env.dev` và `.env.prod`
- ✅ Không cần duplicate code cho từng environment

---

## 🔧 Setup lần đầu

### 1. Tạo Discord Bot cho DEV (miễn phí)

Truy cập: https://discord.com/developers/applications

**Bước 1:** Tạo Application
```
1. Click "New Application"
2. Tên: "Loa phát thanh [DEV]" (hoặc tên bạn thích)
3. Click "Create"
```

**Bước 2:** Setup Bot
```
1. Tab "Bot" → Click "Add Bot" → Confirm
2. Scroll xuống "Privileged Gateway Intents":
   ☑ Message Content Intent (bắt buộc!)
   ☐ Presence Intent (không cần)
   ☐ Server Members Intent (không cần)
3. Click "Save Changes"
4. Scroll lên trên, click "Reset Token" → Copy token DEV
   ⚠️ Lưu token này vào nơi an toàn (Notepad/1Password)
```

**Bước 3:** Mời Bot DEV vào server test
```
1. Tab "OAuth2" → "URL Generator"
2. Chọn Scopes:
   ☑ bot
   ☑ applications.commands
3. Chọn Bot Permissions:
   ☑ Read Messages/View Channels
   ☑ Send Messages
   ☑ Read Message History
   ☑ Connect (Voice)
   ☑ Speak (Voice)
4. Copy URL ở dưới → Mở trình duyệt → Chọn server TEST → Authorize
```

**Lưu ý:** Bot DEV chỉ invite vào server test, KHÔNG invite vào server production.

---

### 2. Setup môi trường Local (PC)

**Đảm bảo đã cài:**
- ✅ Python 3.11+ (`python --version`)
- ✅ Git (`git --version`)
- ✅ FFmpeg (`ffmpeg -version`)
- ✅ Virtual environment đã tạo (`venv` folder có sẵn)

**Nếu chưa có venv:**
```powershell
cd "C:\Users\duywi\Documents\DiscordBot\Loa phát thanh\TTS-Vietnamese-Discord-bot"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🧪 Quy trình Development

### Chạy Bot DEV trên PC

```powershell
# Lần đầu: Tạo file .env.dev từ template
Copy-Item config\.env.dev.example .env.dev
notepad .env.dev  # Mở và paste token DEV

# Activate venv
.\venv\Scripts\Activate.ps1

# Chạy bot (tự động nhận .env.dev!)
python src\tts_bot.py
```

**Bot tự động:**
- ✅ Phát hiện file `.env.dev` nếu có
- ✅ Load token DEV
- ✅ Hiển thị: `📝 Loaded environment from: .env.dev`

**Để dừng bot:** `Ctrl + C`

**Để force chạy PROD local (test):**
```powershell
$env:ENV = "prod"
python src\tts_bot.py  # Load .env.prod thay vì .env.dev
```

---

## ✅ Checklist Test (trước khi deploy Production)

Phải test **TẤT CẢ** các bước này trên DEV:

### Test cơ bản (15 phút)
```
□ Bot connect thành công (kiểm tra log)
□ !tts xin chào mọi người (tiếng Việt)
□ !tts en hello world (tiếng Anh)
□ !tts ja こんにちは (tiếng Nhật)
□ !tts ko 안녕하세요 (tiếng Hàn)
□ !tts fr bonjour (tiếng Pháp)
□ !tts de guten tag (tiếng Đức)
□ !tts es hola (tiếng Tây Ban Nha)
□ !tts zh 你好 (tiếng Trung)
```

### Test lệnh quản lý (5 phút)
```
□ !skip - bỏ qua TTS
□ !queue - xem hàng đợi
□ !clear - xóa hàng đợi
□ !leave - bot rời voice
□ !huongdan - hiển thị help
```

### Test edge cases (10 phút)
```
□ Bot tự rời khi không còn ai trong voice channel
□ Bot tự rời sau 1 phút không hoạt động
□ Gửi văn bản >200 ký tự (phải báo lỗi)
□ 2-3 người cùng dùng !tts (queue hoạt động đúng)
□ User rời voice giữa chừng (bot không crash)
□ Gửi !tts mà không ở voice channel (phải báo lỗi)
```

### Quan sát logs (5 phút)
```
□ Không có ERROR trong console
□ ✅ FFmpeg found
□ ✅ Opus loaded (hoặc warning - bình thường trên Windows)
□ TTS file được tạo và cleanup thành công
```

**Tổng thời gian test tối thiểu: 35 phút**

Nếu 1 trong các test FAIL → FIX ngay, test lại từ đầu.

---

## 🚀 Deploy lên Production (Cybrance)

### Bước 1: Đảm bảo code ổn định

```powershell
# Commit code đã test kỹ
git add .
git commit -m "feat: add new feature (tested 35min on DEV)"
```

**Convention commit messages:**
- `feat: ...` - Tính năng mới
- `fix: ...` - Sửa bug
- `docs: ...` - Cập nhật documentation
- `refactor: ...` - Tái cấu trúc code
- `perf: ...` - Cải thiện performance

### Bước 2: Push lên GitHub

```powershell
git push origin main
```

⚠️ **Sau khi push:** Cybrance sẽ **TỰ ĐỘNG** build và deploy trong ~2-3 phút.

### Bước 3: Verify Production

**Trên Cybrance Dashboard:**
1. Vào Project → Deployments
2. Đợi status = "Running" (màu xanh)
3. Click "View Logs" → Kiểm tra:
   ```
   ✅ FFmpeg found
   ✅ Opus loaded
   ✅ Bot đã kết nối thành công
   ```

**Trên Discord:**
1. Bot production phải online (màu xanh)
2. Test nhanh 2-3 lệnh cơ bản:
   - `!tts xin chào`
   - `!tts en hello`
   - `!huongdan`

**Monitor production 1 giờ đầu** để đảm bảo không có issue.

---

## 🔄 Rollback nếu Production lỗi

Nếu sau khi deploy production có bug nghiêm trọng:

### Cách 1: Revert commit cuối (khuyến nghị)

```powershell
# Xem lịch sử commit
git log --oneline

# Revert commit lỗi (tạo commit mới đảo ngược thay đổi)
git revert HEAD
git push origin main
```

Cybrance sẽ tự động deploy lại version cũ trong 2-3 phút.

### Cách 2: Reset về commit cũ (nhanh nhưng mạo hiểm)

```powershell
# Tìm commit ID tốt cuối cùng
git log --oneline

# Reset về commit đó (VD: abc1234)
git reset --hard abc1234

# Force push (⚠️ cẩn thận!)
git push -f origin main
```

**Lưu ý:** Force push sẽ xóa lịch sử commit. Chỉ dùng khi khẩn cấp.

---

## 📝 Best Practices

### Khi code tính năng mới
1. ✅ Tạo branch riêng (optional nhưng tốt):
   ```powershell
   git checkout -b feature/ten-tinh-nang
   # Code xong...
   git checkout main
   git merge feature/ten-tinh-nang
   git push origin main
   ```

2. ✅ Commit nhỏ, thường xuyên:
   - Mỗi tính năng = 1 commit
   - Commit message rõ ràng
   - Dễ rollback nếu cần

3. ✅ Backup trước khi deploy quan trọng:
   ```powershell
   git tag v1.0.0-backup
   git push origin v1.0.0-backup
   ```

### Khi gặp lỗi Production
1. ❌ **KHÔNG** panic code fix trực tiếp trên main
2. ✅ Rollback về version cũ ngay lập tức
3. ✅ Fix bug trên branch DEV, test kỹ
4. ✅ Deploy lại sau khi đã test

### Monitoring Production
- Check logs Cybrance **mỗi ngày** (hoặc setup alert)
- Monitor Discord bot status (online/offline)
- Đọc feedback từ users về bug/issue

---

## 🎯 Quick Reference

### Chạy DEV local
```powershell
.\venv\Scripts\Activate.ps1
python src\tts_bot.py  # Tự động load .env.dev
```

### Deploy Production
```powershell
git add .
git commit -m "feat: your message"
git push origin main
```

### Rollback Production
```powershell
git revert HEAD
git push origin main
```

---

## 🔐 Security

**QUAN TRỌNG:**
- ❌ **KHÔNG** commit file `.env` lên GitHub
- ❌ **KHÔNG** share Discord token công khai
- ✅ Token DEV và PROD phải **KHÁC NHAU**
- ✅ Mỗi token chỉ dùng cho 1 environment

**Kiểm tra `.gitignore` có dòng:**
```
.env
venv/
__pycache__/
*.pyc
*.log
```

---

## 📞 Troubleshooting

### Bot DEV không connect local
```
Lỗi: "Discord token not found"
Fix: Kiểm tra $env:Discord_Token đã set đúng token chưa
```

### Production không deploy sau push
```
Lỗi: Cybrance stuck "Building..."
Fix: 1. Check Dockerfile syntax
     2. Check requirements.txt đúng format
     3. View build logs trên Cybrance
```

### Bot crash khi dùng !tts
```
Lỗi: "FFmpeg not found"
Fix: Đảm bảo Dockerfile có: apt-get install ffmpeg libopus0
```

### Token bị leak lên GitHub
```
Hành động: 1. Vào Discord Developer Portal
          2. Regenerate token NGAY LẬP TỨC
          3. Update token mới trên Cybrance
          4. Xóa commit chứa token cũ khỏi Git history
```

---

## 📚 Tài nguyên

- **Discord Developer Portal:** https://discord.com/developers/applications
- **Cybrance Dashboard:** https://cybrance.io (hoặc URL hosting của bạn)
- **GitHub Repository:** https://github.com/MonsieurNikko/TTS-Vietnamese-Discord-bot
- **Discord.py Docs:** https://discordpy.readthedocs.io/

---

**✅ Workflow này đảm bảo production luôn ổn định, không downtime, dễ rollback!**
