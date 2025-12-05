import os
import threading
from flask import Flask
import discord
from discord.ext import commands

TOKEN = os.environ.get("DISCORD_TOKEN")

TARGET_MESSAGE_ID = 1446599486909714482
TARGET_ROLE_ID = 1446592229102719137
TARGET_EMOJI = "✅"

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

app = Flask(__name__)

@app.route("/")
def home():
    return "ok"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user} ({bot.user.id})")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.guild_id is None:
        return
    if payload.message_id != TARGET_MESSAGE_ID:
        return
    if str(payload.emoji) != TARGET_EMOJI:
        return
    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return
    role = guild.get_role(TARGET_ROLE_ID)
    if role is None:
        print("role not found")
        return
    if payload.user_id == bot.user.id:
        return
    member = guild.get_member(payload.user_id)
    if member is None:
        try:
            member = await guild.fetch_member(payload.user_id)
        except Exception as e:
            print("fetch_member error:", e)
            return
    if member.bot:
        return
    try:
        await member.add_roles(role, reason="Reaction role")
        print(f"Added role {role.id} to {member} ({member.id})")
    except Exception as e:
        print("add_roles error:", e)

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    bot.run(TOKEN)
