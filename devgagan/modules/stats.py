import time
import sys
import motor
from devgagan import app
from pyrogram import filters
from pyrogram.enums import ParseMode
from config import OWNER_ID
from devgagan.core.mongo.users_db import get_users, add_user, get_user
from devgagan.core.mongo.plans_db import premium_users

start_time = time.time()

# -------------------- Track Users --------------------
@app.on_message(group=10)
async def chat_watcher_func(_, message):
    try:
        if message.from_user:
            us_in_db = await get_user(message.from_user.id)
            if not us_in_db:
                await add_user(message.from_user.id)
    except:
        pass

# -------------------- Uptime Formatter --------------------
def time_formatter():
    minutes, seconds = divmod(int(time.time() - start_time), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    tmp = (
        ((str(weeks) + "w:") if weeks else "")
        + ((str(days) + "d:") if days else "")
        + ((str(hours) + "h:") if hours else "")
        + ((str(minutes) + "m:") if minutes else "")
        + ((str(seconds) + "s") if seconds else "")
    )
    if tmp != "":
        if tmp.endswith(":"):
            return tmp[:-1]
        else:
            return tmp
    else:
        return "0 s"

# -------------------- Stats Command --------------------
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats(client, message):
    start = time.time()
    users = await get_users()
    premium = await premium_users()
    ping = round((time.time() - start) * 1000)

    # -------------------- Premium Users List with HTML links --------------------
    premium_list = []
    if premium:
        for user_id in premium:
            try:
                user = await client.get_users(user_id)
                name = user.first_name or "Unknown"
                # HTML link to user's Telegram profile
                premium_list.append(f'<a href="tg://user?id={user_id}">{name}</a>')
            except:
                # fallback if user info cannot be fetched
                premium_list.append(f'<a href="tg://user?id={user_id}">Unknown</a>')
    else:
        premium_list = ["None"]

    # -------------------- Reply with Stats --------------------
    await message.reply_text(f"""
Stats of {(await client.get_me()).mention} :

🏓 Ping Pong: {ping}ms
📊 Total Users : {len(users)}
📈 Premium Users : {len(premium)}
💎 Premium Users : {', '.join(premium_list)}
⚙️ Bot Uptime : {time_formatter()}

🎨 Python Version: {sys.version.split()[0]}
📑 Mongo Version: {motor.version}
""", parse_mode=ParseMode.HTML)
