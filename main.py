
import os
import asyncio
import discord
import yt_dlp
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

queues = {}
ydl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    "default_search": "ytsearch1:"
}

async def get_song(query):
    loop = asyncio.get_running_loop()
    def extract():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if "entries" in info:
                info = info["entries"][0]
            return {
                "title": info["title"],
                "url": info["url"]
            }
    return await loop.run_in_executor(None, extract)

async def play_next(guild):
    queue = queues.get(guild.id, [])
    voice = guild.voice_client

    if not queue or not voice:
        return

    song = queue.pop(0)
    source = discord.FFmpegPCMAudio(
        song["url"],
        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        options="-vn"
    )

    def after(error):
        asyncio.run_coroutine_threadsafe(
            play_next(guild), bot.loop
        )

    voice.play(source, after=after)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("i3zfv7 is online!")

@bot.tree.command(name="play", description="تشغيل أغنية")
async def play(interaction: discord.Interaction, song: str):
    await interaction.response.defer()

    if not interaction.user.voice:
        return await interaction.followup.send("ادخل روم صوتي أولاً")

    voice = interaction.guild.voice_client
    if not voice:
        voice = await interaction.user.voice.channel.connect()

    try:
        track = await get_song(song)
        queue = queues.setdefault(interaction.guild.id, [])

        if voice.is_playing() or voice.is_paused():
            queue.append(track)
            await interaction.followup.send(
                f"أضيفت للقائمة: **{track['title']}**"
            )
        else:
            queue.append(track)
            await play_next(interaction.guild)
            await interaction.followup.send(
                f"يتم التشغيل: **{track['title']}** 🎵"
            )
    except Exception:
        await interaction.followup.send("تعذر العثور على الأغنية")

@bot.tree.command(name="skip", description="تخطي الأغنية")
async def skip(interaction: discord.Interaction):
    voice = interaction.guild.voice_client
    if voice and voice.is_playing():
        voice.stop()
        await interaction.response.send_message("تم التخطي ⏭️")
    else:
        await interaction.response.send_message("ما فيه أغنية تعمل")

@bot.tree.command(name="pause", description="إيقاف مؤقت")
async def pause(interaction: discord.Interaction):
    voice = interaction.guild.voice_client
    if voice and voice.is_playing():
        voice.pause()
        await interaction.response.send_message("تم الإيقاف المؤقت")
    else:
        await interaction.response.send_message("ما فيه أغنية تعمل")

@bot.tree.command(name="resume", description="استكمال الأغنية")
async def resume(interaction: discord.Interaction):
    voice = interaction.guild.voice_client
    if voice and voice.is_paused():
        voice.resume()
        await interaction.response.send_message("تم الاستكمال 🎵")
    else:
        await interaction.response.send_message("ما فيه أغنية متوقفة")

@bot.tree.command(name="queue", description="عرض قائمة الأغاني")
async def queue(interaction: discord.Interaction):
    songs = queues.get(interaction.guild.id, [])
    if not songs:
        return await interaction.response.send_message("القائمة فارغة")

    names = "\n".join(
        f"{i+1}. {s['title']}" for i, s in enumerate(songs[:10])
    )
    await interaction.response.send_message(f"🎵 **قائمة الانتظار:**\n{names}")

@bot.tree.command(name="stop", description="إيقاف ومسح القائمة")
async def stop(interaction: discord.Interaction):
    voice = interaction.guild.voice_client
    queues[interaction.guild.id] = []

    if voice:
        voice.stop()

    await interaction.response.send_message("تم إيقاف الموسيقى ومسح القائمة")

@bot.tree.command(name="leave", description="خروج البوت")
async def leave(interaction: discord.Interaction):
    voice = interaction.guild.voice_client
    queues[interaction.guild.id] = []

    if voice:
        await voice.disconnect()
        await interaction.response.send_message("مع السلامة 🎵")
    else:
        await interaction.response.send_message("أنا لست في روم صوتي")

bot.run(os.getenv("DISCORD_TOKEN"))
