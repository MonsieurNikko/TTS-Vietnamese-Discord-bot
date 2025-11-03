import discord
from discord.ext import commands, tasks
import os
import time
import logging
from dotenv import load_dotenv
from gtts import gTTS
import tempfile
from collections import defaultdict
import asyncio
import subprocess
import shutil
import json
import glob
from pathlib import Path

# Load environment variables with smart detection
def load_environment():
    """Load environment variables from appropriate .env file"""
    # Priority order:
    # 1. ENV environment variable (e.g., ENV=dev, ENV=prod)
    # 2. .env.dev if exists (development)
    # 3. .env.prod if exists (production)
    # 4. .env (default)
    
    env_mode = os.getenv('ENV', '').lower()
    
    # Check parent directory (project root)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    env_files = []
    
    if env_mode == 'dev':
        env_files.append(os.path.join(root_dir, '.env.dev'))
    elif env_mode == 'prod':
        env_files.append(os.path.join(root_dir, '.env.prod'))
    elif env_mode.startswith('bot'):  # bot1, bot2, bot3, etc.
        env_files.append(os.path.join(root_dir, f'.env.{env_mode}'))
    else:
        # Auto-detect: prefer .env.dev if exists (development mode)
        env_files.append(os.path.join(root_dir, '.env.dev'))
        env_files.append(os.path.join(root_dir, '.env.prod'))
    
    # Always fallback to .env
    env_files.append(os.path.join(root_dir, '.env'))
    
    # Load first existing file
    for env_file in env_files:
        if os.path.exists(env_file):
            load_dotenv(env_file)
            env_name = os.path.basename(env_file)
            print(f"📝 Loaded environment from: {env_name}")
            return env_name
    
    # No .env file found, try load_dotenv() default
    load_dotenv()
    print("📝 Using default environment variables")
    return "default"

# Load environment
loaded_env = load_environment()

# Determine bot priority from loaded environment
BOT_PRIORITY = 999  # Default: lowest priority
if loaded_env.startswith('.env.bot'):
    try:
        bot_num = loaded_env.replace('.env.bot', '')
        BOT_PRIORITY = int(bot_num)
    except:
        BOT_PRIORITY = 999

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format=f'%(asctime)s - [BOT {BOT_PRIORITY}] - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Multi-bot coordination file
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOT_STATUS_FILE = os.path.join(PROJECT_ROOT, 'bot_status.json')

def get_bot_status():
    """Read current bot status from coordination file"""
    try:
        if os.path.exists(BOT_STATUS_FILE):
            with open(BOT_STATUS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Clean old entries (>5 seconds old)
                current_time = time.time()
                data = {k: v for k, v in data.items() if current_time - v.get('last_update', 0) < 5}
                return data
    except Exception as e:
        logger.error(f"Error reading bot status: {e}")
    return {}

def update_bot_status(guild_id, is_busy):
    """Update this bot's status in coordination file"""
    try:
        status = get_bot_status()
        bot_key = f"bot{BOT_PRIORITY}"
        
        if is_busy:
            status[bot_key] = {
                'priority': BOT_PRIORITY,
                'guild_id': guild_id,
                'is_busy': True,
                'last_update': time.time()
            }
        else:
            # Remove this bot's status when not busy
            status.pop(bot_key, None)
        
        with open(BOT_STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2)
    except Exception as e:
        logger.error(f"Error updating bot status: {e}")

def should_this_bot_respond(guild_id):
    """Check if this bot should respond based on priority"""
    status = get_bot_status()
    
    # Check if any higher priority bot is handling this guild
    for bot_key, bot_data in status.items():
        if bot_data.get('guild_id') == guild_id:
            bot_priority = bot_data.get('priority', 999)
            if bot_priority < BOT_PRIORITY:
                # Higher priority bot is already handling this
                logger.info(f"Higher priority bot (Bot {bot_priority}) is handling guild {guild_id}")
                return False
    
    # No higher priority bot is handling this guild
    return True

logger.info(f"🎯 Bot Priority: {BOT_PRIORITY}")

# Check FFmpeg availability
def check_ffmpeg():
    """Check if ffmpeg is installed"""
    if shutil.which('ffmpeg'):
        logger.info("✅ FFmpeg found")
        return True
    logger.error("❌ FFmpeg not found! Install: apt-get install ffmpeg")
    return False

def check_opus():
    """Check and load Opus library"""
    try:
        if not discord.opus.is_loaded():
            # Try common opus library locations
            for lib in ['libopus.so.0', '/usr/lib/x86_64-linux-gnu/libopus.so.0', 
                       '/usr/lib/libopus.so.0', 'opus.dll', 'libopus-0.dll']:
                try:
                    discord.opus.load_opus(lib)
                    if discord.opus.is_loaded():
                        logger.info(f"✅ Opus loaded: {lib}")
                        return True
                except:
                    continue
            logger.error("❌ Opus NOT loaded! Install: apt-get install libopus0")
            return False
        logger.info("✅ Opus already loaded")
        return True
    except Exception as e:
        logger.error(f"❌ Opus error: {e}")
        return False

# Check dependencies on startup
check_ffmpeg()
check_opus()

# Configuration
class Config:
    TOKEN = os.getenv('Discord_Token')
    PREFIX = ''  # Không có prefix, chỉ cần gõ tên lệnh
    TIMEOUT_MINUTES = 1  # Bot tự out sau 1 phút không hoạt động
    MAX_TEXT_LENGTH = 200
    TEMP_DIR = tempfile.gettempdir()
    ANNOUNCE_USERNAME = False  # Chỉ hiện tên trong chat, không đọc TTS
    DEFAULT_LANGUAGE = 'vi'    # Ngôn ngữ mặc định

# Ngôn ngữ hỗ trợ (mã ngắn -> mã gTTS)
SUPPORTED_LANGS = {
    'vi': 'vi',
    'en': 'en',
    'ja': 'ja',
    'ko': 'ko',
    'fr': 'fr',
    'de': 'de',
    'es': 'es',
    'zh': 'zh-CN'
}

# Setup intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=Config.PREFIX, intents=intents)

# Bot state
voice_clients = {}
last_activity = defaultdict(float)
tts_queue = defaultdict(list)  # mỗi phần tử: (text, channel_id, lang)
processing = defaultdict(bool)

class TTSBot:
    def __init__(self):
        self.temp_files = set()
    
    async def create_tts_audio(self, text: str, lang='vi') -> str:
        """Create TTS audio file and return path"""
        try:
            # Create TTS object
            tts = gTTS(text=text, lang=lang, slow=False)
            
            # Create temporary file
            temp_file = os.path.join(Config.TEMP_DIR, f"tts_{int(time.time())}_{hash(text)}.mp3")
            
            # Save TTS to file
            tts.save(temp_file)
            self.temp_files.add(temp_file)
            
            logger.info(f"Created TTS file: {temp_file}")
            return temp_file
            
        except Exception as e:
            logger.error(f"Error creating TTS: {e}")
            return None
    
    async def cleanup_temp_file(self, file_path: str):
        """Clean up temporary file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.temp_files.discard(file_path)
                logger.info(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up file {file_path}: {e}")
    
    async def process_tts_queue(self, guild_id: int):
        """Process TTS queue for a specific guild"""
        if processing[guild_id] or not tts_queue[guild_id]:
            return
        
        processing[guild_id] = True
        
        try:
            while tts_queue[guild_id]:
                item = tts_queue[guild_id].pop(0)
                # Backward compatible: (text, channel_id) hoặc (text, channel_id, lang)
                if len(item) == 2:
                    text, channel_id = item
                    lang = Config.DEFAULT_LANGUAGE
                else:
                    text, channel_id, lang = item
                
                if guild_id not in voice_clients:
                    break
                
                voice_client = voice_clients[guild_id]
                
                # Create TTS audio
                audio_file = await self.create_tts_audio(text, lang=lang)
                if not audio_file:
                    continue
                
                # Play audio
                try:
                    # FFmpeg options (simple, compatible with all versions)
                    ffmpeg_options = {
                        'options': '-vn'
                    }
                    
                    audio_source = discord.FFmpegPCMAudio(
                        audio_file,
                        **ffmpeg_options
                    )
                    
                    # Create done event
                    done = asyncio.Event()
                    
                    def after_playing(error):
                        if error:
                            logger.error(f"Error in audio playback: {error}")
                        done.set()
                    
                    voice_client.play(audio_source, after=after_playing)
                    
                    # Wait for audio to finish with timeout
                    try:
                        await asyncio.wait_for(done.wait(), timeout=30.0)
                    except asyncio.TimeoutError:
                        logger.warning("Audio playback timed out")
                        if voice_client.is_playing():
                            voice_client.stop()
                    
                    # Update last activity
                    last_activity[guild_id] = time.time()
                    
                except discord.ClientException as e:
                    logger.error(f"Discord client error playing audio: {e}")
                except Exception as e:
                    logger.error(f"Error playing audio: {e}", exc_info=True)
                
                finally:
                    # Clean up temp file
                    await self.cleanup_temp_file(audio_file)
                
                # Small delay between messages
                await asyncio.sleep(0.5)
        
        except Exception as e:
            logger.error(f"Error processing TTS queue: {e}")
        
        finally:
            processing[guild_id] = False

# Create TTS bot instance
tts_bot = TTSBot()

@bot.event
async def on_ready():
    logger.info(f'{bot.user} đã kết nối thành công!')
    logger.info(f'Bot đang hoạt động trên {len(bot.guilds)} server(s)')
    
    # Start cleanup task
    cleanup_inactive_connections.start()

@bot.event
async def on_voice_state_update(member, before, after):
    """Handle voice state updates"""
    if member == bot.user:
        return
    
    # If user left the channel and bot is in a voice channel
    if before.channel and bot.user in before.channel.members:
        # Check if bot is alone in the channel (no human members)
        human_members = [m for m in before.channel.members if not m.bot]
        if len(human_members) == 0:
            guild_id = before.channel.guild.id
            # Disconnect immediately when alone
            if guild_id in voice_clients:
                try:
                    await voice_clients[guild_id].disconnect()
                    logger.info(f"Auto-disconnected from {before.channel.name} - no members left")
                    
                    # Clean up
                    del voice_clients[guild_id]
                    if guild_id in last_activity:
                        del last_activity[guild_id]
                    if guild_id in tts_queue:
                        tts_queue[guild_id].clear()
                    
                    # 🎯 Mark bot as not busy
                    update_bot_status(guild_id, is_busy=False)
                except Exception as e:
                    logger.error(f"Error auto-disconnecting: {e}")

@bot.command(name='tts', aliases=['Tts', 'TTS'])
async def text_to_speech(ctx, *, text: str = None):
    """Main TTS command"""
    guild_id = ctx.guild.id
    
    # 🎯 MULTI-BOT PRIORITY CHECK
    if not should_this_bot_respond(guild_id):
        # Higher priority bot is handling this guild - silently ignore
        logger.info(f"Skipping TTS request - higher priority bot is active")
        return
    
    if not text:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Vui lòng nhập văn bản cần đọc!\nVí dụ: `!tts Xin chào mọi người`",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Check text length
    if len(text) > Config.MAX_TEXT_LENGTH:
        embed = discord.Embed(
            title="❌ Văn bản quá dài",
            description=f"Văn bản không được vượt quá {Config.MAX_TEXT_LENGTH} ký tự.\nHiện tại: {len(text)} ký tự",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Check if user is in voice channel
    if not ctx.author.voice:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn cần vào voice channel trước khi sử dụng TTS!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    voice_channel = ctx.author.voice.channel
    
    try:
        # Check if bot is in different voice channel
        if guild_id in voice_clients and voice_clients[guild_id].is_connected():
            current_channel = voice_clients[guild_id].channel
            if current_channel.id != voice_channel.id:
                # Bot is in different channel - mark as busy
                update_bot_status(guild_id, is_busy=True)
                embed = discord.Embed(
                    title=f"⚠️ Bot {BOT_PRIORITY} đang bận!",
                    description=f"🔊 Tôi đang hoạt động ở: **{current_channel.name}**\n\n💡 Bot khác sẽ xử lý request của bạn!",
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed)
                return
        
        # 🎯 Mark this bot as busy BEFORE connecting
        update_bot_status(guild_id, is_busy=True)
        
        # Connect to voice channel if not already connected
        if guild_id not in voice_clients or not voice_clients[guild_id].is_connected():
            voice_client = await voice_channel.connect()
            voice_clients[guild_id] = voice_client
            
            embed = discord.Embed(
                title=f"🔊 Bot {BOT_PRIORITY} đã kết nối",
                description=f"Đã kết nối vào **{voice_channel.name}**",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        
        # Phân tích ngôn ngữ ở đầu câu: ví dụ "en hello" -> lang=en, content="hello"
        detected_lang = Config.DEFAULT_LANGUAGE
        content = text.strip()
        if ' ' in content:
            maybe_code, rest = content.split(' ', 1)
            code = maybe_code.lower()
            if code in SUPPORTED_LANGS and rest.strip():
                detected_lang = SUPPORTED_LANGS[code]
                content = rest.strip()

        # Re-check text length after removing lang code
        if len(content) > Config.MAX_TEXT_LENGTH:
            embed = discord.Embed(
                title="❌ Văn bản quá dài",
                description=f"Văn bản không được vượt quá {Config.MAX_TEXT_LENGTH} ký tự.\nHiện tại: {len(content)} ký tự",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Bot chỉ đọc text thuần (không đọc tên người dùng)
        full_text = content
        
        # Add to queue with full text và ngôn ngữ
        tts_queue[guild_id].append((full_text, ctx.channel.id, detected_lang))
        last_activity[guild_id] = time.time()
        
        # Show queue status - Hiện tên người dùng trong chat (không đọc TTS)
        queue_length = len(tts_queue[guild_id])
        if queue_length > 1:
            embed = discord.Embed(
                title="📝 Đã thêm vào hàng đợi",
                description=f"👤 **{ctx.author.display_name}**: `{content[:50]}{'...' if len(content) > 50 else ''}`\n🌐 Ngôn ngữ: `{detected_lang}`\n📍 Vị trí: {queue_length}",
                color=discord.Color.blue()
            )
        else:
            embed = discord.Embed(
                title="🔊 Đang phát",
                description=f"👤 **{ctx.author.display_name}**: `{content[:50]}{'...' if len(content) > 50 else ''}`\n🌐 Ngôn ngữ: `{detected_lang}`",
                color=discord.Color.green()
            )
        
        await ctx.send(embed=embed)
        
        # Process queue
        await tts_bot.process_tts_queue(guild_id)
        
    except discord.errors.ClientException as e:
        if "already connected" in str(e):
            # Bot is already connected to a different channel
            current_channel = voice_clients[guild_id].channel
            embed = discord.Embed(
                title="⚠️ Cảnh báo",
                description=f"Bot đang hoạt động trong **{current_channel.name}**\nHãy vào channel đó hoặc đợi bot rảnh!",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        else:
            logger.error(f"Discord client error: {e}")
            embed = discord.Embed(
                title="❌ Lỗi kết nối",
                description="Không thể kết nối vào voice channel. Vui lòng thử lại!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    except Exception as e:
        logger.error(f"Error in TTS command: {e}")
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Đã xảy ra lỗi khi xử lý TTS. Vui lòng thử lại!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command(name='skip')
async def skip_tts(ctx):
    """Skip current TTS"""
    guild_id = ctx.guild.id
    
    if guild_id not in voice_clients:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bot không có trong voice channel nào!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    voice_client = voice_clients[guild_id]
    
    if voice_client.is_playing():
        voice_client.stop()
        embed = discord.Embed(
            title="⏭️ Đã bỏ qua",
            description="Đã bỏ qua TTS hiện tại",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="ℹ️ Thông báo",
            description="Bot không đang phát âm thanh nào",
            color=discord.Color.blue()
        )
    
    await ctx.send(embed=embed)

@bot.command(name='queue')
async def show_queue(ctx):
    """Show TTS queue"""
    guild_id = ctx.guild.id
    
    if not tts_queue[guild_id]:
        embed = discord.Embed(
            title="📝 Hàng đợi TTS",
            description="Hàng đợi trống",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        return
    
    queue_text = ""
    for i, item in enumerate(tts_queue[guild_id][:10], 1):
        if len(item) == 2:
            text_item, _ = item
            lang = Config.DEFAULT_LANGUAGE
        else:
            text_item, _, lang = item
        queue_text += f"**{i}.** `{text_item[:50]}{'...' if len(text_item) > 50 else ''}` • 🌐 `{lang}`\n"
    
    if len(tts_queue[guild_id]) > 10:
        queue_text += f"\n... và {len(tts_queue[guild_id]) - 10} mục khác"
    
    embed = discord.Embed(
        title="📝 Hàng đợi TTS",
        description=queue_text,
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Tổng cộng: {len(tts_queue[guild_id])} mục")
    
    await ctx.send(embed=embed)

@bot.command(name='clear')
async def clear_queue(ctx):
    """Clear TTS queue"""
    guild_id = ctx.guild.id
    
    if not tts_queue[guild_id]:
        embed = discord.Embed(
            title="ℹ️ Thông báo",
            description="Hàng đợi đã trống",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        return
    
    cleared_count = len(tts_queue[guild_id])
    tts_queue[guild_id].clear()
    
    embed = discord.Embed(
        title="🗑️ Đã xóa",
        description=f"Đã xóa {cleared_count} mục trong hàng đợi",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='leave')
async def leave_voice(ctx):
    """Leave voice channel"""
    guild_id = ctx.guild.id
    
    if guild_id not in voice_clients:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bot không có trong voice channel nào!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    voice_client = voice_clients[guild_id]
    channel_name = voice_client.channel.name
    
    # Clear queue and disconnect
    tts_queue[guild_id].clear()
    await voice_client.disconnect()
    del voice_clients[guild_id]
    
    if guild_id in last_activity:
        del last_activity[guild_id]
    
    # 🎯 Mark bot as not busy
    update_bot_status(guild_id, is_busy=False)
    
    embed = discord.Embed(
        title=f"👋 Bot {BOT_PRIORITY} đã rời khỏi",
        description=f"Đã rời khỏi **{channel_name}**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='huongdan', aliases=['hd', 'guide'])
async def help_command(ctx):
    """Show help message"""
    embed = discord.Embed(
        title="🤖 Hướng dẫn sử dụng TTS Bot",
        description="Bot Text-to-Speech hỗ trợ 8 ngôn ngữ với các lệnh sau:",
        color=discord.Color.blue()
    )
    
    # Lệnh TTS cơ bản
    embed.add_field(
        name="**🎤 TTS cơ bản**",
        value="**tts <văn bản>** - Đọc bằng tiếng Việt (mặc định)\nVí dụ: `tts Xin chào mọi người`\n`tts Hôm nay trời đẹp quá`",
        inline=False
    )
    
    # TTS với ngôn ngữ khác
    embed.add_field(
        name="**🌐 TTS đa ngôn ngữ**",
        value="**tts <mã_ngôn_ngữ> <văn bản>** - Đọc bằng ngôn ngữ chỉ định\n\n"
              "**Danh sách ngôn ngữ:**\n"
              "• `vi` - Tiếng Việt (mặc định)\n"
              "• `en` - English (Tiếng Anh)\n"
              "• `ja` - 日本語 (Tiếng Nhật)\n"
              "• `ko` - 한국어 (Tiếng Hàn)\n"
              "• `fr` - Français (Tiếng Pháp)\n"
              "• `de` - Deutsch (Tiếng Đức)\n"
              "• `es` - Español (Tiếng Tây Ban Nha)\n"
              "• `zh` - 中文 (Tiếng Trung)\n\n"
              "**Ví dụ:**\n"
              "`tts en hello everyone`\n"
              "`tts ja こんにちは`\n"
              "`tts ko 안녕하세요`\n"
              "`tts fr bonjour`",
        inline=False
    )
    
    # Lệnh quản lý
    commands_list = [
        ("**skip** hoặc **s**", "Bỏ qua TTS đang phát hiện tại"),
        ("**queue** hoặc **q**", "Xem danh sách TTS đang chờ"),
        ("**clear** hoặc **c**", "Xóa toàn bộ hàng đợi TTS"),
        ("**leave**", "Bot rời khỏi voice channel"),
    ]
    
    embed.add_field(
        name="**⚙️ Quản lý Queue**",
        value="\n".join([f"{cmd} - {desc}" for cmd, desc in commands_list]),
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Lưu ý:",
        value=f"• Văn bản tối đa {Config.MAX_TEXT_LENGTH} ký tự\n"
              "• Bot tự động rời sau 1 phút không hoạt động\n"
              "• Bot tự động rời khi không còn ai trong voice\n"
              "• Nếu không ghi mã ngôn ngữ, bot sẽ đọc tiếng Việt\n"
              "• Bot hoạt động trên nhiều server cùng lúc",
        inline=False
    )
    
    embed.set_footer(text="Bot TTS đa ngôn ngữ 🌏 • Gõ !huongdan để xem hướng dẫn")
    await ctx.send(embed=embed)

@tasks.loop(minutes=1)
async def cleanup_inactive_connections():
    """Clean up inactive voice connections"""
    current_time = time.time()
    to_remove = []
    
    for guild_id, voice_client in voice_clients.items():
        # Check if connection is still valid
        if not voice_client.is_connected():
            to_remove.append(guild_id)
            continue
        
        # Check inactivity timeout
        if guild_id in last_activity:
            inactive_time = current_time - last_activity[guild_id]
            if inactive_time > (Config.TIMEOUT_MINUTES * 60):
                try:
                    channel_name = voice_client.channel.name
                    await voice_client.disconnect()
                    logger.info(f"Auto-disconnected from {channel_name} due to inactivity")
                except:
                    pass
                to_remove.append(guild_id)
    
    # Clean up disconnected clients
    for guild_id in to_remove:
        if guild_id in voice_clients:
            del voice_clients[guild_id]
        if guild_id in last_activity:
            del last_activity[guild_id]
        if guild_id in tts_queue:
            tts_queue[guild_id].clear()
        if guild_id in processing:
            processing[guild_id] = False
        
        # 🎯 Mark bot as not busy
        update_bot_status(guild_id, is_busy=False)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    
    logger.error(f"Command error: {error}")
    
    embed = discord.Embed(
        title="❌ Lỗi",
        description="Đã xảy ra lỗi khi thực hiện lệnh. Vui lòng thử lại!",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    if not Config.TOKEN:
        logger.error("Discord token not found in .env file!")
    else:
        try:
            bot.run(Config.TOKEN)
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")