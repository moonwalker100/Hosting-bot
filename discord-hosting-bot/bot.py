import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

@bot.command()
async def start(ctx):
    await ctx.send("Bot is working!")

bot.run("YOUR_BOT_TOKEN_HERE")
