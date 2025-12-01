import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("8576488730:AAGwqegAa4GGcYPL_FZT78Uf1x_iGjnyD7k")
OWNER_ID = int(os.getenv("BOT_OWNER_ID", "1718481517"))

# rest of your code...

TOKEN = os.getenv("8576488730:AAGwqegAa4GGcYPL_FZT78Uf1x_iGjnyD7k")
OWNER_ID = int(os.getenv("BOT_OWNER_ID", "1718481517"))

DATA_FILE = "data.json"

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Load or create data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {
        "premium_users": [],
        "fsub_channels": [],
        "user_bots": {}
    }

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def is_premium(user_id):
    return user_id in data["premium_users"]

def can_host_more(user_id):
    limit = 5 if is_premium(user_id) else 1
    return len(data["user_bots"].get(str(user_id), [])) < limit

async def check_fsub(ctx):
    if ctx.author.id == OWNER_ID:
        return True
    if not data["fsub_channels"]:
        return True
    for ch_id in data["fsub_channels"]:
        channel = ctx.guild.get_channel(ch_id)
        if channel and channel.permissions_for(ctx.author).view_channel:
            return True
    await ctx.send("❌ You must join the required channel(s) to use this bot.")
    return False

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

@bot.command()
async def start(ctx):
    if not await check_fsub(ctx):
        return
    await ctx.send(f"Hello {ctx.author.mention}, welcome! Use /upload to upload your bot.")

@bot.command()
async def upload(ctx):
    if not await check_fsub(ctx):
        return
    if not can_host_more(ctx.author.id):
        await ctx.send("❌ You have reached your hosting limit.")
        return
    # For now, just a dummy confirmation
    user_bots = data["user_bots"].setdefault(str(ctx.author.id), [])
    bot_id = len(user_bots) + 1
    user_bots.append({"bot_id": bot_id})
    save_data()
    await ctx.send(f"✅ Your bot #{bot_id} is now hosted!")

@bot.command()
async def delbot(ctx, bot_id: int = None):
    if not await check_fsub(ctx):
        return
    user_bots = data["user_bots"].get(str(ctx.author.id), [])
    if not user_bots:
        await ctx.send("❌ You don't have any hosted bots.")
        return
    if bot_id is None:
        # If no bot_id given, delete the last bot
        removed = user_bots.pop()
        save_data()
        await ctx.send(f"✅ Bot #{removed['bot_id']} deleted.")
        return
    for bot_info in user_bots:
        if bot_info["bot_id"] == bot_id:
            user_bots.remove(bot_info)
            save_data()
            await ctx.send(f"✅ Bot #{bot_id} deleted.")
            return
    await ctx.send("❌ Bot ID not found.")

@bot.command()
async def newbot(ctx):
    if not await check_fsub(ctx):
        return
    await ctx.send("🆕 Use /upload to upload your new bot.")

# Owner-only commands

@bot.command()
async def addpremuser(ctx, user: discord.User):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Only owner can add premium users.")
        return
    if user.id not in data["premium_users"]:
        data["premium_users"].append(user.id)
        save_data()
        await ctx.send(f"✅ Added {user.mention} as premium user.")
    else:
        await ctx.send(f"{user.mention} is already a premium user.")

@bot.command()
async def delpremuser(ctx, user: discord.User):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Only owner can delete premium users.")
        return
    if user.id in data["premium_users"]:
        data["premium_users"].remove(user.id)
        save_data()
        await ctx.send(f"✅ Removed {user.mention} from premium users.")
    else:
        await ctx.send(f"{user.mention} is not a premium user.")

@bot.command()
async def fsubadd(ctx, channel: discord.TextChannel):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Only owner can add FSUB channels.")
        return
    if channel.id not in data["fsub_channels"]:
        data["fsub_channels"].append(channel.id)
        save_data()
        await ctx.send(f"✅ Added {channel.mention} as FSUB channel.")
    else:
        await ctx.send(f"{channel.mention} is already an FSUB channel.")

@bot.command()
async def fsubdel(ctx, channel: discord.TextChannel):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Only owner can remove FSUB channels.")
        return
    if channel.id in data["fsub_channels"]:
        data["fsub_channels"].remove(channel.id)
        save_data()
        await ctx.send(f"✅ Removed {channel.mention} from FSUB channels.")
    else:
        await ctx.send(f"{channel.mention} is not an FSUB channel.")

@bot.command()
async def restart(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Only owner can restart the bot.")
        return
    await ctx.send("🔄 Restarting bot...")
    await bot.close()

bot.run(TOKEN)
