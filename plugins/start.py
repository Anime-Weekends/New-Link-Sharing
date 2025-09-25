import asyncio
import base64
import time
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.errors import FloodWait

from bot import Bot
from config import *
from database.database import *
from plugins.newpost import revoke_invite_after_5_minutes
from helper_func import *


# Broadcast variables
cancel_lock = asyncio.Lock()
is_canceled = False

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.enums import ParseMode
import asyncio
from datetime import datetime, timedelta

# your existing imports stay here (database, revoke_invite_after_5_minutes, etc.)


from pyrogram.enums import ParseMode

from database.database import (
    add_user, save_invite_link,
    get_channel_by_encoded_link, get_channel_by_encoded_link2,
    get_current_invite_link
)

# Track banned users for spam protection
user_banned_until = {}

@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Bot, message: Message):
    user_id = message.from_user.id

    if user_id in user_banned_until:
        if datetime.now() < user_banned_until[user_id]:
            return await message.reply_text(
                "<b><blockquote expandable>You are temporarily banned from using commands due to spamming. Try again later.</b>",
                parse_mode=ParseMode.HTML
            )
            
    await add_user(user_id)

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
                return await message.reply_text(
                    "<b><blockquote expandable>Invalid or expired invite link.</b>",
                    parse_mode=ParseMode.HTML
                )

            # Check if this is a /genlink link (original_link exists)
            from database.database import get_original_link
            original_link = await get_original_link(channel_id)
            if original_link:
                button = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("• Proceed to Link •", url=original_link)]]
                )
                return await message.reply_text(
                    "<b><blockquote expandable>ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ! ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ</b>",
                    reply_markup=button,
                    parse_mode=ParseMode.HTML
                )

            old_link_info = await get_current_invite_link(channel_id)
            if old_link_info:
                try:
                    await client.revoke_chat_invite_link(channel_id, old_link_info["invite_link"])
                    print(f"Revoked old {'request' if old_link_info['is_request'] else 'invite'} link for channel {channel_id}")
                except Exception as e:
                    print(f"Failed to revoke old link for channel {channel_id}: {e}")

            invite = await client.create_chat_invite_link(
                chat_id=channel_id,
                expire_date=datetime.now() + timedelta(minutes=5),
                creates_join_request=is_request
            )

            await save_invite_link(channel_id, invite.invite_link, is_request)

            button_text = "• ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ •" if is_request else "• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •"
            button = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=invite.invite_link)]])

            wait_msg = await message.reply_text(
                "<b>Please wait...</b>",
                parse_mode=ParseMode.HTML
            )
            
            await asyncio.sleep(0.5)
            await wait_msg.delete()
            
            await message.reply_text(
                "<b><blockquote expandable>ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ! ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ</b>",
                reply_markup=button,
                parse_mode=ParseMode.HTML
            )

            note_msg = await message.reply_text(
                "<u><b>Note: If the link is expired, please click the post link again to get a new one.</b></u>",
                parse_mode=ParseMode.HTML
            )

            # Auto-delete the note message after 5 minutes
            asyncio.create_task(delete_after_delay(note_msg, 300))
            asyncio.create_task(revoke_invite_after_5_minutes(client, channel_id, invite.invite_link, is_request))

        except Exception as e:
            await message.reply_text(
                "<b><blockquote expandable>Invalid or expired invite link.</b>",
                parse_mode=ParseMode.HTML
            )
            print(f"Decoding error: {e}")
    else:
        inline_buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="about"),
                 InlineKeyboardButton("• ᴄʜᴀɴɴᴇʟs", callback_data="channels")],
                [InlineKeyboardButton("• Close •", callback_data="close")]
            ]
        )
        
        try:
            await message.reply_photo(
                photo=START_PIC,
                caption=START_MSG,
                reply_markup=inline_buttons,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            print(f"Error sending start picture: {e}")
            await message.reply_text(
                START_MSG,
                reply_markup=inline_buttons,
                parse_mode=ParseMode.HTML
            )



WAIT_MSG = "<b>Processing...</b>"
REPLY_ERROR = "<code>Use this command as a reply to any Telegram message without any spaces.</code>"


@Bot.on_message(filters.command('status') & filters.private & is_owner_or_admin)
async def info(client: Bot, message: Message):
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("• Close •", callback_data="close")]])

    start_time = time.time()
    temp_msg = await message.reply("<b><i>Processing...</i></b>", quote=True, parse_mode=ParseMode.HTML)
    end_time = time.time()

    ping_time = (end_time - start_time) * 1000
    users = await full_userbase()
    delta = datetime.now() - client.uptime
    bottime = get_readable_time(delta.seconds)

    await temp_msg.edit(
        f"<b>Users: {len(users)}\n\nUptime: {bottime}\n\nPing: {ping_time:.2f} ms</b>",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )


@Bot.on_message(filters.command('broadcast') & filters.private & is_owner_or_admin)
async def send_text(client: Bot, message: Message):
    global is_canceled
    async with cancel_lock:
        is_canceled = False
    mode = False
    broad_mode = ''
    store = message.text.split()[1:]

    if store and store[0] == 'silent':
        mode = True
        broad_mode = 'Silent '

    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = len(query)
        successful = blocked = deleted = unsuccessful = 0

        pls_wait = await message.reply("<i>Broadcasting message... This will take some time.</i>", parse_mode=ParseMode.HTML)
        bar_length = 20
        progress_bar = last_update_percentage = percent_complete = 0
        update_interval = 0.05

        for i, chat_id in enumerate(query, start=1):
            async with cancel_lock:
                if is_canceled:
                    break
            try:
                await broadcast_msg.copy(chat_id, disable_notification=mode)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await broadcast_msg.copy(chat_id, disable_notification=mode)
                successful += 1
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

        final_status = f"""<b>🤖 {broad_mode}Broadcast Completed ✅

Progress: [{progress_bar}] {percent_complete:.0%}

Total Users: {total}
Successful: {successful}
Blocked Users: {blocked}
Deleted Accounts: {deleted}
Unsuccessful: {unsuccessful}</b>"""
        return await pls_wait.edit(final_status, parse_mode=ParseMode.HTML)

    else:
        msg = await message.reply(REPLY_ERROR, parse_mode=ParseMode.HTML)
        await asyncio.sleep(8)
        await msg.delete()


@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    if data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    elif data == "about":
        await query.edit_message_media(
            InputMediaPhoto(
                "https://envs.sh/Wdj.jpg",
                ABOUT_TXT
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('• Back', callback_data='start'),
                 InlineKeyboardButton('Close •', callback_data='close')]
            ]),
        )

    elif data == "channels":
        await query.edit_message_media(
            InputMediaPhoto("https://envs.sh/Wdj.jpg", CHANNELS_TXT),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('• Back', callback_data='start'),
                 InlineKeyboardButton('Home•', callback_data='setting')]
            ]),
        )

    elif data in ["start", "home"]:
        inline_buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("• About", callback_data="about"),
                 InlineKeyboardButton("• Channels", callback_data="channels")],
                [InlineKeyboardButton("• Close •", callback_data="close")]
            ]
        )
        try:
            await query.edit_message_media(
                InputMediaPhoto(START_PIC, START_MSG),
                reply_markup=inline_buttons
            )
        except:
            await query.edit_message_text(
                START_MSG,
                reply_markup=inline_buttons,
                parse_mode=ParseMode.HTML
            )


def delete_after_delay(msg, delay):
    async def inner():
        await asyncio.sleep(delay)
        try:
            await msg.delete()
        except:
            pass
    return inner()
