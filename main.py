
import discord
from discord import app_commands
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("i3zfv7 is online!")

@bot.tree.command(name="join", description="دخول الروم الصوتي")
async def join(interaction: discord.Interaction):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message("دخلت الروم 🎵")
    else:
        await interaction.response.send_message("ادخل روم صوتي أولاً")

@bot.tree.command(name="leave", description="الخروج من الروم")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("تم الخروج")
    else:
        await interaction.response.send_message("أنا مو في روم صوتي")

bot.run(os.getenv("DISCORD_TOKEN"))
