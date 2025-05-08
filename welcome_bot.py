from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import json

# Web server for Render
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

Thread(target=run_web).start()

# Environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
if not TOKEN or not CHANNEL_ID:
    raise ValueError("DISCORD_TOKEN or CHANNEL_ID not set")

CHANNEL_ID = int(CHANNEL_ID)

# Load known members
KNOWN_MEMBERS_FILE = "known_members.json"
try:
    with open(KNOWN_MEMBERS_FILE, "r") as f:
        known_members = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    known_members = []

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print(f"Bot is online as {client.user}")

def generate_image(member, message):
    try:
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        response = requests.get(avatar_url)
        avatar = Image.open(BytesIO(response.content)).resize((128, 128))
    except:
        avatar = Image.new("RGB", (128, 128), (255, 255, 255))

    base = Image.new("RGBA", (500, 250), (30, 30, 30, 255))
    draw = ImageDraw.Draw(base)

    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except OSError:
        font = ImageFont.load_default()

    base.paste(avatar, (30, 60))
    draw.text((180, 80), message, font=font, fill=(255, 255, 255))
    draw.text((180, 120), "from TN Clan Master", font=font, fill=(200, 200, 255))

    buffer = BytesIO()
    base.save(buffer, format="PNG")
    buffer.seek(0)
    return discord.File(fp=buffer, filename="message.png")

@client.event
async def on_member_join(member):
    try:
        channel = client.get_channel(CHANNEL_ID)
        if not channel:
            print("Channel not found.")
            return

        welcome_msg = f"Welcome back {member.name}!" if member.id in known_members else f"Welcome {member.name}!"
        file = generate_image(member, welcome_msg)
        await channel.send(f"{welcome_msg} {member.mention} to **TN Clan Master**!", file=file)

        if member.id not in known_members:
            known_members.append(member.id)
            with open(KNOWN_MEMBERS_FILE, "w") as f:
                json.dump(known_members, f)
    except Exception as e:
        print(f"[ERROR in on_member_join] {e}")

@client.event
async def on_member_remove(member):
    try:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            file = generate_image(member, f"Goodbye {member.name}")
            await channel.send(f"{member.name} has left the server. See you again!", file=file)
    except Exception as e:
        print(f"[ERROR in on_member_remove] {e}")

client.run(TOKEN)
