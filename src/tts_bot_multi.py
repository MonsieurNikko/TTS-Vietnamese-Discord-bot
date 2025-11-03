"""
Multi-Bot TTS Orchestrator
Runs multiple bot instances in a single process with smart priority coordination.
"""

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
import glob

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Check FFmpeg and Opus (shared for all bots)
def check_ffmpeg():
    if shutil.which('ffmpeg'):
        logging.info("✅ FFmpeg found")
        return True
    logging.error("❌ FFmpeg not found! Install: apt-get install ffmpeg")
    return False

def check_opus():
    try:
        if not discord.opus.is_loaded():
            for lib in ['libopus.so.0', '/usr/lib/x86_64-linux-gnu/libopus.so.0', 
                       '/usr/lib/libopus.so.0', 'opus.dll', 'libopus-0.dll']:
                try:
                    discord.opus.load_opus(lib)
                    if discord.opus.is_loaded():
                        logging.info(f"✅ Opus loaded: {lib}")
                        return True
                except:
                    continue
            logging.warning("⚠️ Opus NOT loaded (Voice may not work)")
            return False
        logging.info("✅ Opus already loaded")
        return True
    except Exception as e:
        logging.warning(f"⚠️ Opus warning: {e}")
        return False

check_ffmpeg()
check_opus()

# Configuration
SUPPORTED_LANGS = {
    'vi': 'Tiếng Việt',
    'en': 'English',
    'ja': '日本語',
    'ko': '한국어',
    'fr': 'Français',
    'de': 'Deutsch',
    'es': 'Español',
    'zh': '中文'
}

MAX_TEXT_LENGTH = 200
DEFAULT_LANGUAGE = 'vi'
TIMEOUT_MINUTES = 1

class TTSBotInstance:
    """Individual TTS Bot instance with priority"""
    
    def __init__(self, bot_name, token, priority, all_bots_ref):
        self.bot_name = bot_name
        self.token = token
        self.priority = priority
        self.all_bots = all_bots_ref  # Reference to all bot instances
        
        # Create bot
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        self.bot = commands.Bot(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        # Bot state
        self.voice_clients = {}
        self.tts_queue = defaultdict(list)
        self.is_processing = defaultdict(bool)
        self.last_activity = {}
        
        # Setup logger
        self.logger = logging.getLogger(f'Bot{priority}')
        
        # Register events and commands
        self._setup_events()
        self._setup_commands()
        self._setup_tasks()
    
    def is_busy_in_guild(self, guild_id):
        """Check if this bot is busy in a specific guild"""
        return guild_id in self.voice_clients and self.voice_clients[guild_id].is_connected()
    
    def should_respond(self, guild_id):
        """
        Check if this bot should respond based on priority.
        Returns True if:
        1. No higher priority bot is handling this guild
        2. OR all higher priority bots are busy in other guilds
        """
        # Check all bots with higher priority
        for other_bot in self.all_bots:
            if other_bot.priority < self.priority:  # Higher priority (lower number)
                # If higher priority bot is not busy OR busy in same guild (can take over)
                if not other_bot.is_busy_in_guild(guild_id):
                    # Higher priority bot is available
                    if other_bot.is_busy_in_any_guild():
                        # Higher priority bot is busy elsewhere - we can respond
                        continue
                    else:
                        # Higher priority bot is free - they should respond
                        return False
        
        return True
    
    def is_busy_in_any_guild(self):
        """Check if bot is busy in any guild"""
        return any(vc.is_connected() for vc in self.voice_clients.values())
    
    def _setup_events(self):
        @self.bot.event
        async def on_ready():
            self.logger.info(f'🤖 {self.bot.user.name} online! Priority: {self.priority}')
            self.logger.info(f'📊 Connected to {len(self.bot.guilds)} server(s)')
        
        @self.bot.event
        async def on_voice_state_update(member, before, after):
            if member == self.bot.user:
                return
            
            # Auto-disconnect when alone
            if before.channel and self.bot.user in before.channel.members:
                human_members = [m for m in before.channel.members if not m.bot]
                if len(human_members) == 0:
                    guild_id = before.channel.guild.id
                    if guild_id in self.voice_clients:
                        try:
                            await self.voice_clients[guild_id].disconnect()
                            self.logger.info(f"👋 Auto-disconnected from {before.channel.name} - alone")
                            
                            del self.voice_clients[guild_id]
                            self.last_activity.pop(guild_id, None)
                            self.tts_queue[guild_id].clear()
                        except Exception as e:
                            self.logger.error(f"Error auto-disconnecting: {e}")
    
    def _setup_commands(self):
        @self.bot.command(name='tts', aliases=['Tts', 'TTS'])
        async def tts_command(ctx, *, text: str = None):
            await self._handle_tts(ctx, text)
        
        @self.bot.command(name='skip')
        async def skip_command(ctx):
            await self._handle_skip(ctx)
        
        @self.bot.command(name='queue')
        async def queue_command(ctx):
            await self._handle_queue(ctx)
        
        @self.bot.command(name='clear')
        async def clear_command(ctx):
            await self._handle_clear(ctx)
        
        @self.bot.command(name='leave')
        async def leave_command(ctx):
            await self._handle_leave(ctx)
        
        @self.bot.command(name='huongdan')
        async def help_command(ctx):
            await self._handle_help(ctx)
    
    def _setup_tasks(self):
        @tasks.loop(minutes=1)
        async def cleanup_task():
            current_time = time.time()
            to_remove = []
            
            for guild_id, vc in list(self.voice_clients.items()):
                if not vc.is_connected():
                    to_remove.append(guild_id)
                    continue
                
                if guild_id in self.last_activity:
                    inactive_time = current_time - self.last_activity[guild_id]
                    if inactive_time > (TIMEOUT_MINUTES * 60):
                        try:
                            await vc.disconnect()
                            self.logger.info(f"⏰ Auto-disconnected due to inactivity")
                        except:
                            pass
                        to_remove.append(guild_id)
            
            for guild_id in to_remove:
                self.voice_clients.pop(guild_id, None)
                self.last_activity.pop(guild_id, None)
                self.tts_queue[guild_id].clear()
                self.is_processing[guild_id] = False
        
        @cleanup_task.before_loop
        async def before_cleanup():
            await self.bot.wait_until_ready()
        
        cleanup_task.start()
    
    async def _handle_tts(self, ctx, text):
        guild_id = ctx.guild.id
        
        # Priority check
        if not self.should_respond(guild_id):
            self.logger.debug(f"Skipping - higher priority bot available for guild {guild_id}")
            return
        
        if not text:
            embed = discord.Embed(
                title="❌ Lỗi",
                description="Vui lòng nhập văn bản!\nVí dụ: `!tts xin chào`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if len(text) > MAX_TEXT_LENGTH:
            embed = discord.Embed(
                title="❌ Văn bản quá dài",
                description=f"Tối đa {MAX_TEXT_LENGTH} ký tự. Hiện tại: {len(text)} ký tự",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if not ctx.author.voice:
            embed = discord.Embed(
                title="❌ Lỗi",
                description="Bạn cần vào voice channel trước!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        voice_channel = ctx.author.voice.channel
        
        # Check if busy in different channel
        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_connected():
            current_channel = self.voice_clients[guild_id].channel
            if current_channel.id != voice_channel.id:
                embed = discord.Embed(
                    title=f"⚠️ Bot {self.priority} đang bận",
                    description=f"🔊 Đang ở: **{current_channel.name}**\n💡 Bot khác sẽ xử lý!",
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed)
                return
        
        # Connect if needed
        if guild_id not in self.voice_clients or not self.voice_clients[guild_id].is_connected():
            self.voice_clients[guild_id] = await voice_channel.connect()
            embed = discord.Embed(
                title=f"🔊 Bot {self.priority} đã kết nối",
                description=f"Đã kết nối vào **{voice_channel.name}**",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        
        # Parse language
        parts = text.split(maxsplit=1)
        if len(parts) >= 2 and parts[0].lower() in SUPPORTED_LANGS:
            lang = parts[0].lower()
            message = parts[1]
        else:
            lang = DEFAULT_LANGUAGE
            message = text
        
        # Add to queue
        self.tts_queue[guild_id].append({
            'text': message,
            'lang': lang,
            'user': ctx.author.display_name,
            'channel': voice_channel
        })
        
        self.last_activity[guild_id] = time.time()
        
        lang_name = SUPPORTED_LANGS.get(lang, lang)
        queue_pos = len(self.tts_queue[guild_id])
        
        embed = discord.Embed(
            title="✅ TTS Added",
            description=f"**Text:** {message}\n**Language:** {lang_name}\n**Position:** {queue_pos}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Bot {self.priority}")
        await ctx.send(embed=embed)
        
        # Process queue
        if not self.is_processing[guild_id]:
            await self._process_queue(guild_id)
    
    async def _process_queue(self, guild_id):
        self.is_processing[guild_id] = True
        
        try:
            while self.tts_queue[guild_id]:
                item = self.tts_queue[guild_id][0]
                vc = self.voice_clients.get(guild_id)
                
                if not vc or not vc.is_connected():
                    vc = await item['channel'].connect()
                    self.voice_clients[guild_id] = vc
                
                try:
                    tts = gTTS(text=item['text'], lang=item['lang'], slow=False)
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                        tts_file = fp.name
                        tts.save(tts_file)
                    
                    audio = discord.FFmpegPCMAudio(tts_file)
                    vc.play(audio)
                    
                    while vc.is_playing():
                        await asyncio.sleep(0.5)
                    
                    try:
                        os.remove(tts_file)
                    except:
                        pass
                    
                    self.tts_queue[guild_id].pop(0)
                
                except Exception as e:
                    self.logger.error(f"TTS error: {e}")
                    self.tts_queue[guild_id].pop(0)
        
        finally:
            self.is_processing[guild_id] = False
            
            # Auto-disconnect if alone
            vc = self.voice_clients.get(guild_id)
            if vc and vc.is_connected():
                if len(vc.channel.members) <= 1:
                    await vc.disconnect()
                    self.voice_clients.pop(guild_id, None)
                    self.logger.info("👋 Left voice (alone)")
    
    async def _handle_skip(self, ctx):
        guild_id = ctx.guild.id
        vc = self.voice_clients.get(guild_id)
        
        if vc and vc.is_playing():
            vc.stop()
            embed = discord.Embed(title="⏭️ Skipped", description="Đã bỏ qua", color=discord.Color.blue())
        else:
            embed = discord.Embed(title="❌ Lỗi", description="Không có TTS nào đang phát", color=discord.Color.red())
        
        embed.set_footer(text=f"Bot {self.priority}")
        await ctx.send(embed=embed)
    
    async def _handle_queue(self, ctx):
        guild_id = ctx.guild.id
        queue = self.tts_queue.get(guild_id, [])
        
        if not queue:
            embed = discord.Embed(title="📋 Queue trống", color=discord.Color.blue())
        else:
            queue_text = "\n".join([
                f"{i+1}. **{item['text']}** ({SUPPORTED_LANGS.get(item['lang'])}) - {item['user']}"
                for i, item in enumerate(queue[:10])
            ])
            embed = discord.Embed(title=f"📋 Queue ({len(queue)} items)", description=queue_text, color=discord.Color.blue())
        
        embed.set_footer(text=f"Bot {self.priority}")
        await ctx.send(embed=embed)
    
    async def _handle_clear(self, ctx):
        guild_id = ctx.guild.id
        count = len(self.tts_queue.get(guild_id, []))
        self.tts_queue[guild_id] = []
        
        embed = discord.Embed(title="🗑️ Đã xóa queue", description=f"Đã xóa {count} items", color=discord.Color.green())
        embed.set_footer(text=f"Bot {self.priority}")
        await ctx.send(embed=embed)
    
    async def _handle_leave(self, ctx):
        guild_id = ctx.guild.id
        vc = self.voice_clients.get(guild_id)
        
        if vc and vc.is_connected():
            await vc.disconnect()
            self.voice_clients.pop(guild_id, None)
            self.tts_queue[guild_id] = []
            
            embed = discord.Embed(title="👋 Đã rời voice", color=discord.Color.green())
        else:
            embed = discord.Embed(title="❌ Lỗi", description="Bot không ở trong voice", color=discord.Color.red())
        
        embed.set_footer(text=f"Bot {self.priority}")
        await ctx.send(embed=embed)
    
    async def _handle_help(self, ctx):
        embed = discord.Embed(
            title="📖 Hướng dẫn sử dụng Loa phát thanh",
            description="Bot TTS đa ngôn ngữ",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎤 Lệnh cơ bản",
            value=(
                "`!tts <text>` - Đọc văn bản (mặc định tiếng Việt)\n"
                "`!tts en <text>` - Đọc tiếng Anh\n"
                "`!tts ja <text>` - Đọc tiếng Nhật\n"
                "`!tts ko <text>` - Đọc tiếng Hàn"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎵 Quản lý",
            value="`!skip` `!queue` `!clear` `!leave`",
            inline=False
        )
        
        langs = ", ".join([f"`{k}` ({v})" for k, v in SUPPORTED_LANGS.items()])
        embed.add_field(name="🌍 Ngôn ngữ", value=langs, inline=False)
        
        embed.set_footer(text=f"Bot {self.priority}")
        await ctx.send(embed=embed)
    
    async def start(self):
        """Start this bot instance"""
        try:
            await self.bot.start(self.token)
        except Exception as e:
            self.logger.error(f"Failed to start: {e}")
            raise


def discover_bot_configs():
    """Discover all .env.botN files and load tokens"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    configs = []
    
    # Find all .env.bot* files
    bot_files = sorted(glob.glob(os.path.join(root_dir, '.env.bot*')))
    
    for env_file in bot_files:
        if env_file.endswith('.example'):
            continue
        
        # Load env file
        load_dotenv(env_file, override=True)
        token = os.getenv('Discord_Token')
        
        if token and 'YOUR_BOT' not in token and 'TOKEN_HERE' not in token:
            bot_name = os.path.basename(env_file)
            
            # Extract priority number
            try:
                priority = int(bot_name.replace('.env.bot', ''))
            except:
                priority = 999
            
            configs.append({
                'name': bot_name,
                'token': token,
                'priority': priority,
                'file': env_file
            })
            logging.info(f"📝 Discovered: {bot_name} (Priority {priority})")
    
    if not configs:
        raise ValueError("❌ No valid bot configs found! Create .env.bot1, .env.bot2, etc.")
    
    # Sort by priority
    configs.sort(key=lambda x: x['priority'])
    return configs


async def main():
    """Main orchestrator - runs all bots concurrently"""
    logging.info("🚀 Starting Multi-Bot TTS Orchestrator...")
    
    # Discover bots
    bot_configs = discover_bot_configs()
    logging.info(f"📊 Found {len(bot_configs)} bot(s)")
    
    # Create bot instances
    bot_instances = []
    for config in bot_configs:
        bot = TTSBotInstance(
            bot_name=config['name'],
            token=config['token'],
            priority=config['priority'],
            all_bots_ref=bot_instances  # Pass reference to all bots
        )
        bot_instances.append(bot)
    
    # Update all bots with complete list
    for bot in bot_instances:
        bot.all_bots = bot_instances
    
    logging.info("✅ All bots initialized with priority coordination")
    
    # Run all bots concurrently
    tasks = [bot.start() for bot in bot_instances]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("👋 Shutting down...")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        raise
