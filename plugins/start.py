# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
#     ✧ R ᴇ x ʏ   -   レクシィ   -   Dᴇᴠ ✧
# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦

import asyncio
from datetime import datetime, timedelta
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    InputMediaPhoto
)

from bot import Bot
from config import *
from database.database import *
from helper_func import *
from plugins.newpost import revoke_invite_after_5_minutes

# ========================= GLOBALS ========================= #
user_message_count = {}
user_banned_until = {}
WAIT_MSG = "<b>Processing...</b>"
REPLY_ERROR = "<code>Use this command as a reply to any Telegram message.</code>"

# ========================= START COMMAND ========================= #
@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Bot, message: Message):
    user_id = message.from_user.id
    now = datetime.now()

    # Check temp ban
    if user_id in user_banned_until and now < user_banned_until[user_id]:
        return await message.reply_text(
            "<b>You are temporarily banned due to spamming. Try later.</b>",
            parse_mode=ParseMode.HTML
        )

    await add_user(user_id)

    # Handle deep-links
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
            is_request = base64_string.startswith("req_")
            if is_request:
                base64_string = base64_string[4:]
                channel_id = await get_channel_by_encoded_link2(base64_string)
            else:
                channel_id = await get_channel_by_encoded_link(base64_string)

            if not channel_id:
                return await message.reply_text("<b>Invalid or expired invite link.</b>", parse_mode=ParseMode.HTML)

            # If permanent link exists
            original_link = await get_original_link(channel_id)
            if original_link:
                button = InlineKeyboardMarkup([[InlineKeyboardButton("• Proceed to Link •", url=original_link)]])
                return await message.reply_text(
                    "<b>Here is your link! Click below to proceed.</b>",
                    reply_markup=button, parse_mode=ParseMode.HTML
                )

            # Revoke old link
            old_link_info = await get_current_invite_link(channel_id)
            if old_link_info:
                try:
                    await client.revoke_chat_invite_link(channel_id, old_link_info["invite_link"])
                except: pass

            # Create new link
            invite = await client.create_chat_invite_link(
                chat_id=channel_id,
                expire_date=datetime.now() + timedelta(minutes=5),
                creates_join_request=is_request
            )
            await save_invite_link(channel_id, invite.invite_link, is_request)

            button_text = "• Request to Join •" if is_request else "• Join Channel •"
            button = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=invite.invite_link)]])

            await message.reply_text(
                "<b>Here is your link! Click below to proceed.</b>",
                reply_markup=button, parse_mode=ParseMode.HTML
            )

            note_msg = await message.reply_text(
                "<u><b>Note: If expired, click the post link again for a new one.</b></u>",
                parse_mode=ParseMode.HTML
            )
            delete_after_delay(note_msg, 300)
            asyncio.create_task(revoke_invite_after_5_minutes(client, channel_id, invite.invite_link, is_request))

        except Exception as e:
            print(f"Start link error: {e}")
            await message.reply_text("<b>Invalid or expired invite link.</b>", parse_mode=ParseMode.HTML)

    else:
        # Normal start (no deep link)
        inline_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("• About", callback_data="about"),
             InlineKeyboardButton("• Channels", callback_data="channels")],
            [InlineKeyboardButton("• Close •", callback_data="close")]
        ])
        try:
            await message.reply_photo(photo=START_PIC, caption=START_MSG,
                                      reply_markup=inline_buttons, parse_mode=ParseMode.HTML)
        except:
            await message.reply_text(START_MSG, reply_markup=inline_buttons, parse_mode=ParseMode.HTML)

# ========================= CALLBACK HANDLERS ========================= #
@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    if data == "close":
        await query.answer()
        try: await query.message.delete()
        except: pass
        return

    elif data in ["about", "channels"]:
        # animate dots
        try:
            for i in range(1, 4):
                dots = "● " * i + "○ " * (3 - i)
                await query.message.edit_text(dots)
                await asyncio.sleep(0.3)
        except: pass

        caption = ABOUT_TXT if data == "about" else CHANNELS_TXT
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("• Back", callback_data="start"),
             InlineKeyboardButton("• Close", callback_data="close")]
        ])
        try:
            await query.message.edit_media(
                InputMediaPhoto(media="https://envs.sh/Wdj.jpg", caption=caption),
                reply_markup=buttons
            )
        except:
            await query.message.edit_text(caption, reply_markup=buttons)

    elif data in ["start", "home"]:
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("• About", callback_data="about"),
             InlineKeyboardButton("• Channels", callback_data="channels")],
            [InlineKeyboardButton("• Close •", callback_data="close")]
        ])
        try:
            await query.message.edit_media(InputMediaPhoto(media=START_PIC, caption=START_MSG),
                                           reply_markup=buttons)
        except:
            await query.message.edit_text(START_MSG, reply_markup=buttons, parse_mode=ParseMode.HTML)

# ========================= SPAM MONITOR ========================= #
MAX_MESSAGES = 3
TIME_WINDOW = timedelta(seconds=10)
BAN_DURATION = timedelta(hours=1)

@Bot.on_message(filters.private)
async def monitor_messages(client: Bot, message: Message):
    user_id = message.from_user.id
    now = datetime.now()

    if message.text and message.text.startswith("/"): return
    if user_id in user_banned_until and now < user_banned_until[user_id]:
        await message.reply_text("<b>You are banned due to spam. Try later.</b>", parse_mode=ParseMode.HTML)
        return

    user_message_count.setdefault(user_id, []).append(now)
    user_message_count[user_id] = [t for t in user_message_count[user_id] if now - t <= TIME_WINDOW]

    if len(user_message_count[user_id]) > MAX_MESSAGES:
        user_banned_until[user_id] = now + BAN_DURATION
        await message.reply_text("<b>You are banned due to spam. Try later.</b>", parse_mode=ParseMode.HTML)

# ========================= UTILS ========================= #
def delete_after_delay(msg, delay):
    async def inner():
        await asyncio.sleep(delay)
        try: await msg.delete()
        except: pass
    asyncio.create_task(inner())
