# 🚀 Development & Release Workflow

**Mục tiêu:** Test an toàn trên PC, deploy lên Cybrance production không sợ crash.

---

## 📋 Tổng quan

| Environment | Chạy ở đâu | Bot Token | Discord Server | Mục đích |
|-------------|-----------|-----------|----------------|----------|
| **Development** | PC local | DEV Token | Server test riêng | Code & test tính năng |
| **Production** | Cybrance | PROD Token | Server chính | User thật sử dụng |
| **Multi-Bot** | PC/Cybrance | BOT1/2/3 Tokens | Cùng 1 server | Join nhiều voice room cùng lúc |

**Nguyên tắc vàng:**
- ✅ Luôn test trên DEV trước
- ❌ Không bao giờ code trực tiếp trên production
- ✅ Deploy production chỉ khi DEV đã test kỹ ≥30 phút
- 🎯 Dùng multi-bot khi cần bot ở nhiều voice channel cùng lúc (1 server)

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

---

## 🤖 Multi-Bot: Join nhiều voice room cùng lúc (Smart Priority)

**Khi nào cần:** Bạn muốn bot ở nhiều voice channel cùng lúc trong 1 server.

**Giới hạn Discord API:** 1 bot chỉ join được 1 voice channel/server.

**Giải pháp:** Tạo nhiều Discord Application (nhiều bot), chạy nhiều instance code với **priority system**.

**⚡ Cơ chế Smart Priority:**
- Bot 1 (ưu tiên cao nhất) sẽ xử lý request đầu tiên
- Khi Bot 1 đang bận (ở voice channel khác), Bot 2 tự động nhận request
- Các bot tự động phối hợp qua file `bot_status.json` (không cần setup thêm gì!)

### 🔧 Setup Multi-Bot (Ví dụ: 3 bot)

#### Bước 1: Tạo 3 Discord Applications

Truy cập: https://discord.com/developers/applications

```
Bot 1: "Loa phát thanh #1"
Bot 2: "Loa phát thanh #2"
Bot 3: "Loa phát thanh #3"
```

Mỗi bot làm giống setup DEV/PROD:
- Bật **Message Content Intent**
- Copy token của từng bot
- Invite vào server (dùng OAuth2 URL Generator)

#### Bước 2: Tạo file `.env` cho từng bot

Trong thư mục gốc project:

**`.env.bot1`** (Voice Room 1)
```env
Discord_Token=TOKEN_CUA_BOT_1_O_DAY
```

**`.env.bot2`** (Voice Room 2)
```env
Discord_Token=TOKEN_CUA_BOT_2_O_DAY
```

**`.env.bot3`** (Voice Room 3)
```env
Discord_Token=TOKEN_CUA_BOT_3_O_DAY
```

#### Bước 3: Chạy Multi-Bot

**Có 2 cách chạy:**

**🌟 Cách 1: Chạy TẤT CẢ bot trong 1 terminal (Khuyến nghị - dùng cho Cybrance)**

```powershell
cd "C:\Users\duywi\Documents\DiscordBot\Loa phát thanh\TTS-Vietnamese-Discord-bot"
.\venv\Scripts\Activate.ps1
python src\tts_bot_multi.py
```

**Output mong đợi:**
```
🚀 Starting Multi-Bot TTS Orchestrator...
📝 Discovered: .env.bot1 (Priority 1)
📝 Discovered: .env.bot2 (Priority 2)
📊 Found 2 bot(s)
✅ All bots initialized with priority coordination
🤖 Loa phát thanh #1 online! Priority: 1
🤖 Loa phát thanh #2 online! Priority: 2
```

**Ưu điểm:**
- ✅ Chỉ cần 1 terminal/container
- ✅ Hoàn hảo cho Cybrance (1 process chạy nhiều bot)
- ✅ Tự động phối hợp priority giữa các bot

---

**📟 Cách 2: Chạy từng bot riêng (Local testing)**

**Terminal 1:** (Bot #1)
```powershell
cd "C:\Users\duywi\Documents\DiscordBot\Loa phát thanh\TTS-Vietnamese-Discord-bot"
.\venv\Scripts\Activate.ps1
$env:ENV="bot1"
python src\tts_bot.py
```

**Terminal 2:** (Bot #2)
```powershell
cd "C:\Users\duywi\Documents\DiscordBot\Loa phát thanh\TTS-Vietnamese-Discord-bot"
.\venv\Scripts\Activate.ps1
$env:ENV="bot2"
python src\tts_bot.py
```

**Ưu điểm:**
- ✅ Dễ debug từng bot riêng
- ✅ Dùng file-based coordination (bot_status.json)

#### Bước 4: Sử dụng trên Discord (Smart Priority)

**Scenario 1: Chỉ 1 voice room hoạt động**
```
User A ở Voice Room 1: !tts xin chào
→ Bot 1 respond (ưu tiên cao nhất)
```

**Scenario 2: 2 voice rooms cùng lúc**
```
User A ở Voice Room 1: !tts xin chào
→ Bot 1 respond và join Room 1

User B ở Voice Room 2: !tts hello
→ Bot 1 đang bận → Bot 2 tự động respond và join Room 2
```

**Scenario 3: 3 voice rooms cùng lúc**
```
Room 1 → Bot 1 xử lý
Room 2 → Bot 2 xử lý (Bot 1 bận)
Room 3 → Bot 3 xử lý (Bot 1 & 2 bận)
```

**✨ Ưu điểm:**
- User không cần quan tâm bot nào respond
- Hệ thống tự động chọn bot rảnh
- Ưu tiên bot số thấp trước (Bot 1 > Bot 2 > Bot 3)

### 🎯 Tips Multi-Bot

**Đặt tên bot dễ nhận biết:**
```
"Loa phát thanh #1" → Avatar màu đỏ
"Loa phát thanh #2" → Avatar màu xanh
"Loa phát thanh #3" → Avatar màu vàng
```

**Quản lý token:**
```
- Lưu 3 token vào file riêng biệt (.env.bot1/2/3)
- Git-ignored tự động (pattern .env.*)
- Không commit token lên GitHub
```

**Hosting trên Cybrance:**

**Option A: Multi-Bot Orchestrator (Khuyến nghị)**
- 1 container chạy **TẤT CẢ bot** cùng lúc
- Dockerfile CMD: `python src/tts_bot_multi.py`
- Tạo `.env.bot1`, `.env.bot2`, `.env.bot3` trong project
- Push lên GitHub → Cybrance auto-deploy → 3 bot cùng chạy!

**Option B: Separate Containers (Phức tạp hơn)**
- Cần 3 container/service riêng trên Cybrance
- Mỗi container set ENV variable: `ENV=bot1`, `ENV=bot2`, `ENV=bot3`
- Dockerfile CMD: `python src/tts_bot.py`

---

## 📚 Tài nguyên

- **Discord Developer Portal:** https://discord.com/developers/applications
- **Cybrance Dashboard:** https://cybrance.io (hoặc URL hosting của bạn)
- **GitHub Repository:** https://github.com/MonsieurNikko/TTS-Vietnamese-Discord-bot
- **Discord.py Docs:** https://discordpy.readthedocs.io/

---

**✅ Workflow này đảm bảo production luôn ổn định, không downtime, dễ rollback!**
