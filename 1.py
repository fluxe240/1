import os
import threading
from flask import Flask
import discord

TOKEN = os.environ["DISCORD_TOKEN"]

MESSAGE_ID = 1446825712609919050
ROLE_ID = 1446592229102719137
EMOJI = "✅"

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.reactions = True

class MyBot(discord.Client):
    async def on_ready(self):
        print(f"READY {self.user} {self.user.id}")

    async def on_raw_reaction_add(self, payload):
        print("REACTION_ADD", payload.message_id, str(payload.emoji), payload.user_id)
        if payload.guild_id is None:
            return
        if payload.message_id != MESSAGE_ID:
            return
        if str(payload.emoji) != EMOJI:
            return
        guild = self.get_guild(payload.guild_id)
        if guild is None:
            return
        role = guild.get_role(ROLE_ID)
        if role is None:
            print("ROLE_NOT_FOUND")
            return
        if payload.user_id == self.user.id:
            return
        member = guild.get_member(payload.user_id)
        if member is None:
            try:
                member = await guild.fetch_member(payload.user_id)
            except Exception as e:
                print("FETCH_ERROR", e)
                return
        if member.bot:
            return
        try:
            await member.add_roles(role, reason="verify reaction add")
            print("ROLE_ADDED", member.id)
        except Exception as e:
            print("ADD_ROLE_ERROR", e)

    async def on_raw_reaction_remove(self, payload):
        print("REACTION_REMOVE", payload.message_id, str(payload.emoji), payload.user_id)
        if payload.guild_id is None:
            return
        if payload.message_id != MESSAGE_ID:
            return
        if str(payload.emoji) != EMOJI:
            return
        guild = self.get_guild(payload.guild_id)
        if guild is None:
            return
        role = guild.get_role(ROLE_ID)
        if role is None:
            print("ROLE_NOT_FOUND")
            return
        if payload.user_id == self.user.id:
            return
        member = guild.get_member(payload.user_id)
        if member is None:
            try:
                member = await guild.fetch_member(payload.user_id)
            except Exception as e:
                print("FETCH_ERROR", e)
                return
        if member.bot:
            return
        try:
            await member.remove_roles(role, reason="verify reaction remove")
            print("ROLE_REMOVED", member.id)
        except Exception as e:
            print("REMOVE_ROLE_ERROR", e)

app = Flask(__name__)

@app.route("/")
def index():
    return "ok"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot = MyBot(intents=intents)
    bot.run(TOKEN)
