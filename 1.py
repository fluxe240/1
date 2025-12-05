import os
import threading
from flask import Flask
import discord

# ============ НАСТРОЙКИ ============

MESSAGE_ID = 1446599486909714482
ROLE_ID = 1446592229102719137
EMOJI = "✅"

# ============ DISCORD INTENTS ============

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.reactions = True

# ============ BOT CLASS ============

class MyBot(discord.Client):
    async def on_ready(self):
        print(f"[BOT] READY {self.user} ({self.user.id})")

    async def on_raw_reaction_add(self, payload):
        print("[BOT] REACTION",
              "msg", payload.message_id,
              "emoji", str(payload.emoji),
              "user", payload.user_id,
              "guild", payload.guild_id)

        if payload.guild_id is None:
            print("[BOT] not in guild -> skip")
            return

        if payload.message_id != MESSAGE_ID:
            print("[BOT] other message -> skip")
            return

        if str(payload.emoji) != EMOJI:
            print("[BOT] other emoji -> skip")
            return

        guild = self.get_guild(payload.guild_id)
        if guild is None:
            print("[BOT] guild is None")
            return

        role = guild.get_role(ROLE_ID)
        if role is None:
            print("[BOT] ROLE_NOT_FOUND", ROLE_ID)
            return

        if payload.user_id == self.user.id:
            print("[BOT] this is bot itself -> skip")
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
            print("[BOT] member is bot -> skip")
            return

        try:
            await member.add_roles(role, reason="verify reaction")
            print("[BOT] ROLE_ADDED", member.id)
        except Exception as e:
            print("[BOT] ADD_ROLE_ERROR", e)

# ============ FLASK ============

app = Flask(__name__)

@app.route("/")
def index():
    return "ok"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    print(f"[WEB] starting on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)

# ============ MAIN ============

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
