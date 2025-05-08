from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os

# Dummy Flask web server for Render
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_web).start()

# Load environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not TOKEN or not CHANNEL_ID:
    raise ValueError("DISCORD_TOKEN or CHANNEL_ID not found. Add them in Render's environment variables.")

CHANNEL_ID = int(CHANNEL_ID)

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print(f"TN Clan Master bot is online as {client.user}")

@client.event
async def on_member_join(member):
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Channel not found!")
        return

    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    response = requests.get(avatar_url)
    avatar = Image.open(BytesIO(response.content)).resize((128, 128))

    base = Image.new("RGBA", (500, 250), (30, 30, 30, 255))
    draw = ImageDraw.Draw(base)
    font = ImageFont.truetype("arial.ttf", 24)

    base.paste(avatar, (30, 60))
    draw.text((180, 80), f"Welcome {member.name}!", font=font, fill=(255, 255, 255))
    draw.text((180, 120), "to TN Clan Master!", font=font, fill=(200, 200, 255))

    buffer = BytesIO()
    base.save(buffer, format="PNG")
    buffer.seek(0)

    file = discord.File(fp=buffer, filename="welcome.png")
    await channel.send(f"Welcome {member.mention} to **TN Clan Master**!", file=file)