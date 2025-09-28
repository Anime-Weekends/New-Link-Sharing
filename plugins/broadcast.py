# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
#     ✧ R ᴇ x y   -   レクシィ   -   Dᴇᴠ ✧
# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦

import asyncio
from datetime import datetime, timedelta
from pyrogram import Client as Bot, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --------------------- GLOBALS --------------------- #

is_canceled = False
cancel_lock = asyncio.Lock()

user_message_count = {}
user_banned_until = {}
user_database = set()  # store chat_ids for broadcasting

REPLY_ERROR = "<code>Use this command as a reply to any Telegram message.</code>"

# ------------------- BROADCAST HELPERS ------------------- #

async def full_userbase():
    """Return all chat IDs for broadcasting"""
    return list(user_database)

async def del_user(chat_id):
    """Remove a user from the broadcast database"""
    user_database.discard(chat_id)

def is_owner_or_admin(_, __, message):
    return message.from_user and message.from_user.id in ADMINS

# ------------------- BROADCAST COMMAND ------------------- #

@Bot.on_message(filters.command('broadcast') & filters.private & is_owner_or_admin)
async def send_text(client: Bot, message: Message):
    global is_canceled
    async with cancel_lock:
        is_canceled = False

    mode = False
    broad_mode = ''
    store = message.text.split()[1:]

    if store and len(store) == 1 and store[0].lower() == 'silent':
        mode = True
        broad_mode = 'Silent '

    if not message.reply_to_message:
        msg = await message.reply(REPLY_ERROR, parse_mode=ParseMode.HTML)
        await asyncio.sleep(8)
        await msg.delete()
        return

    broadcast_msg = message.reply_to_message
    query = await full_userbase()
    total = len(query)
    successful = 0
    blocked = 0
    deleted = 0
    unsuccessful = 0

    pls_wait = await message.reply("<i>Broadcasting message... This may take time.</i>", parse_mode=ParseMode.HTML)

    bar_length = 20
    final_progress_bar = "●" * bar_length
    complete_msg = f"🤖 {broad_mode}Broadcast Completed ✅"
    progress_bar = ''
    last_update_percentage = 0
    percent_complete = 0
    update_interval = 0.05

    for i, chat_id in enumerate(query, start=1):
        async with cancel_lock:
            if is_canceled:
                final_progress_bar = progress_bar
                complete_msg = f"🤖 {broad_mode}Broadcast Canceled ❌"
                break

        try:
            await broadcast_msg.copy(chat_id, disable_notification=mode)
            successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await broadcast_msg.copy(chat_id, disable_notification=mode)
            successful += 1
        except UserIsBlocked:
            await del_user(chat_id)
            blocked += 1
        except InputUserDeactivated:
            await del_user(chat_id)
            deleted += 1
        except:
            unsuccessful += 1

        percent_complete = i / total

        if percent_complete - last_update_percentage >= update_interval or last_update_percentage == 0:
            num_blocks = int(percent_complete * bar_length)
            progress_bar = "●" * num_blocks + "○" * (bar_length - num_blocks)

            status_update = f"""<b>🤖 {broad_mode}Broadcast in Progress...

Progress: [{progress_bar}] {percent_complete:.0%}

Total Users: {total}
Successful: {successful}
Blocked Users: {blocked}
Deleted Accounts: {deleted}
Unsuccessful: {unsuccessful}</b>

<i>To stop the broadcast, use: /cancel</i>"""
            await pls_wait.edit(status_update, parse_mode=ParseMode.HTML)
            last_update_percentage = percent_complete

    final_status = f"""<b>{complete_msg}

Progress: [{final_progress_bar}] {percent_complete:.0%}

Total Users: {total}
Successful: {successful}
Blocked Users: {blocked}
Deleted Accounts: {deleted}
Unsuccessful: {unsuccessful}</b>"""
    await pls_wait.edit(final_status, parse_mode=ParseMode.HTML)

# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
#     ✧ R ᴇ x ʏ   -   レクシィ   -   Dᴇᴠ ✧
# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
