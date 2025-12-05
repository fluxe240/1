import os
import threading
from flask import Flask
import discord
from discord.ext import commands

TOKEN = os.environ["DISCORD_TOKEN"]

TARGET_MESSAGE_ID = 1446599486909714482
TARGET_ROLE_ID = 1446592229102719137
TARGET_EMOJI = "✅"

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_raw_reaction_add(payload):
    print("reaction add:", payload.message_id, str(payload.emoji), payload.user_id)

    if payload.message_id != TARGET_MESSAGE_ID:
        print("wrong message id")
        return

    if str(payload.emoji) != TARGET_EMOJI:
        print("wrong emoji:", str(payload.emoji))
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        print("guild is None")
        return

    role = guild.get_role(TARGET_ROLE_ID)
    if role is None:
        print("role not found")
        return

    if payload.user_id == bot.user.id:
        print("bot reacted, skip")
        return

    member = guild.get_member(payload.user_id)
    if member is None:
        try:
            member = await guild.fetch_member(payload.user_id)
        except Exception as e:
            print("cannot fetch member:", e)
            return

    if member.bot:
        print("member is bot, skip")
        return

    try:
        await member.add_roles(role, reason="Reaction verify")
        print(f"role added to {member} ({member.id})")
    except Exception as e:
        print("error add_roles:", e)

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    bot.run(TOKEN)
