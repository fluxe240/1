import os
import threading
from flask import Flask
import discord

MESSAGE_ID = 1446599486909714482
ROLE_ID = 1446592229102719137
EMOJI = "✅"

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.reactions = True

class MyBot(discord.Client):
    async def on_ready(self):
        print(f"[BOT] READY {self.user} ({self.user.id})")

    async def on_raw_reaction_add(self, payload):
        print("[BOT] REACTION_ADD",
              "msg", payload.message_id,
              "emoji", str(payload.emoji),
              "user", payload.user_id,
              "guild", payload.guild_id)

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
            print("[BOT] ROLE_NOT_FOUND", ROLE_ID)
            return

        if payload.user_id == self.user.id:
            return

        member = guild.get_member(payload.user_id)
        if member is None:
            try:
                member = await guild.fetch_member(payload.user_id)
                print("[BOT] fetched member", member.id)
            except Exception as e:
                print("[BOT] FETCH_ERROR", e)
                return

        if member.bot:
            return

        try:
            await member.add_roles(role, reason="verify reaction add")
            print("[BOT] ROLE_ADDED", member.id)
        except Exception as e:
            print("[BOT] ADD_ROLE_ERROR", e)

    async def on_raw_reaction_remove(self, payload):
        print("[BOT] REACTION_REMOVE",
              "msg", payload.message_id,
              "emoji", str(payload.emoji),
              "user", payload.user_id,
              "guild", payload.guild_id)

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
            print("[BOT] ROLE_NOT_FOUND", ROLE_ID)
            return

        if payload.user_id == self.user.id:
            return

        member = guild.get_member(payload.user_id)
        if member is None:
            try:
                member = await guild.fetch_member(payload.user_id)
                print("[BOT] fetched member", member.id)
            except Exception as e:
                print("[BOT] FETCH_ERROR", e)
                return

        if member.bot:
            return

        try:
            await member.remove_roles(role, reason="verify reaction remove")
            print("[BOT] ROLE_REMOVED", member.id)
        except Exception as e:
            print("[BOT] REMOVE_ROLE_ERROR", e)

app = Flask(__name__)

@app.route("/")
def index():
    return "ok"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    print(f"[WEB] starting on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("[ERROR] DISCORD_TOKEN env var is missing or empty")
        raise SystemExit("No DISCORD_TOKEN")

    print("[MAIN] starting Flask thread")
    threading.Thread(target=run_web, daemon=True).start()

    print("[MAIN] starting Discord bot")
    bot = MyBot(intents=intents)
    bot.run(token)
