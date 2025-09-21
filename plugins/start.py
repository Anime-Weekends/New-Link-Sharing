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

SUPPORT_LINK = "https://t.me/YourSupportLink"


from pyrogram.enums import ParseMode

from database.database import (
    add_user, save_invite_link,
    get_channel_by_encoded_link, get_channel_by_encoded_link2,
    get_current_invite_link
)

# Track banned users for spam protection
user_banned_until = {}

SUPPORT_LINK = "https://t.me/YourSupportLink"


# ========= HELPERS ========= #
async def delete_after_delay(msg: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass


async def revoke_invite_after_5_minutes(client, channel_id, invite_link, is_request):
    await asyncio.sleep(300)
    try:
        await client.revoke_chat_invite_link(channel_id, invite_link)
    except:
        pass


async def safe_edit_message(query: CallbackQuery, text: str, reply_markup=None):
    """
    Tries to edit caption first (for photo messages),
    then falls back to text edits.
    """
    try:
        await query.message.edit_caption(
            caption=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except Exception:
        try:
            await query.message.edit_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
        except:
            await query.answer("⚠️ Message not modified.", show_alert=False)


# ========= START COMMAND ========= #
@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Bot, message: Message):
    user_id = message.from_user.id

    # anti-spam ban check
    if user_id in user_banned_until and datetime.now() < user_banned_until[user_id]:
        return await message.reply_text(
            "<b><blockquote expandable>You are temporarily banned from using commands due to spamming. Try again later.</b>",
            parse_mode=ParseMode.HTML
        )

    await add_user(user_id)

    text = message.text
    if len(text) > 7:
        # ---- invite link logic ---- #
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

            from database.database import get_original_link
            original_link = await get_original_link(channel_id)
            if original_link:
                button = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("• Proceed to Link •", url=original_link)]]
                )
                return await message.reply_text(
                    "<b><blockquote expandable>Here is your link! Click below to proceed</b>",
                    reply_markup=button,
                    parse_mode=ParseMode.HTML
                )

            old_link_info = await get_current_invite_link(channel_id)
            if old_link_info:
                try:
                    await client.revoke_chat_invite_link(channel_id, old_link_info["invite_link"])
                except Exception as e:
                    print(f"Failed to revoke old link: {e}")

            invite = await client.create_chat_invite_link(
                chat_id=channel_id,
                expire_date=datetime.now() + timedelta(minutes=5),
                creates_join_request=is_request
            )
            await save_invite_link(channel_id, invite.invite_link, is_request)

            button_text = "• Request to Join •" if is_request else "• Join Channel •"
            button = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=invite.invite_link)]])

            wait_msg = await message.reply_text("<b>Please wait...</b>", parse_mode=ParseMode.HTML)
            await asyncio.sleep(0.5)
            await wait_msg.delete()

            await message.reply_text(
                "<b><blockquote expandable>Here is your link! Click below to proceed</b>",
                reply_markup=button,
                parse_mode=ParseMode.HTML
            )

            note_msg = await message.reply_text(
                "<u><b>Note: If the link is expired, please click the post link again to get a new one.</b></u>",
                parse_mode=ParseMode.HTML
            )
            asyncio.create_task(delete_after_delay(note_msg, 300))
            asyncio.create_task(revoke_invite_after_5_minutes(client, channel_id, invite.invite_link, is_request))

        except Exception as e:
            await message.reply_text(
                "<b><blockquote expandable>Invalid or expired invite link.</b>",
                parse_mode=ParseMode.HTML
            )
            print(f"Decoding error: {e}")

    else:
        # start menu with buttons
        inline_buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("• More Commands •", callback_data="more_1")],
                [InlineKeyboardButton("About", callback_data="about"),
                 InlineKeyboardButton("Channels", callback_data="channels")],
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
        except:
            await message.reply_text(
                START_MSG,
                reply_markup=inline_buttons,
                parse_mode=ParseMode.HTML
            )


# ========= CALLBACK HANDLER ========= #
@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    # ---- Close ---- #
    if data == "close":
        try:
            await query.message.delete()
        except:
            await query.answer("❌ Can't close this panel.", show_alert=True)

    # ---- About ---- #
    elif data == "about":
        await safe_edit_message(
            query,
            "<b>ℹ️ About:\n\nThis bot helps you manage invite links and broadcasts.</b>",
            InlineKeyboardMarkup(
                [[InlineKeyboardButton("Back", callback_data="home"),
                  InlineKeyboardButton("Support", url=SUPPORT_LINK)]]
            )
        )

    # ---- Channels ---- #
    elif data == "channels":
        await safe_edit_message(
            query,
            "<b>📢 Channels:\n\nHere you will find the official channels list.</b>",
            InlineKeyboardMarkup(
                [[InlineKeyboardButton("Back", callback_data="home"),
                  InlineKeyboardButton("Support", url=SUPPORT_LINK)]]
            )
        )

    # ---- Home ---- #
    elif data == "home":
        inline_buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("• More Commands •", callback_data="more_1")],
                [InlineKeyboardButton("About", callback_data="about"),
                 InlineKeyboardButton("Channels", callback_data="channels")],
                [InlineKeyboardButton("• Close •", callback_data="close")]
            ]
        )
        await safe_edit_message(query, START_MSG, inline_buttons)

    # ---- More Commands (Page 1) ---- #
    elif data == "more_1":
        buttons = [
            [InlineKeyboardButton("1", callback_data="cmd_1"),
             InlineKeyboardButton("2", callback_data="cmd_2"),
             InlineKeyboardButton("3", callback_data="cmd_3")],
            [InlineKeyboardButton("4", callback_data="cmd_4"),
             InlineKeyboardButton("5", callback_data="cmd_5"),
             InlineKeyboardButton("6", callback_data="cmd_6")],
            [InlineKeyboardButton("7", callback_data="cmd_7"),
             InlineKeyboardButton("8", callback_data="cmd_8"),
             InlineKeyboardButton("9", callback_data="cmd_9")],
            [InlineKeyboardButton("<", callback_data="home"),
             InlineKeyboardButton("Home", callback_data="home"),
             InlineKeyboardButton(">", callback_data="more_2")]
        ]
        await safe_edit_message(query, "<b>📜 More Commands - Page 1</b>", InlineKeyboardMarkup(buttons))

    # ---- More Commands (Page 2) ---- #
    elif data == "more_2":
        buttons = [
            [InlineKeyboardButton("10", callback_data="cmd_10"),
             InlineKeyboardButton("11", callback_data="cmd_11")],
            [InlineKeyboardButton("12", callback_data="cmd_12")],
            [InlineKeyboardButton("<", callback_data="more_1"),
             InlineKeyboardButton("Home", callback_data="home"),
             InlineKeyboardButton(">", callback_data="more_3")]
        ]
        await safe_edit_message(query, "<b>📜 More Commands - Page 2</b>", InlineKeyboardMarkup(buttons))

    # ---- More Commands (Page 3) ---- #
    elif data == "more_3":
        await safe_edit_message(
            query,
            "<b>📜 More Commands - Page 3\n\n(You can add more buttons here if needed)</b>",
            InlineKeyboardMarkup(
                [[InlineKeyboardButton("<", callback_data="more_2"),
                  InlineKeyboardButton("Home", callback_data="home")]]
            )
        )

    # ---- All Command Buttons ---- #
    elif data.startswith("cmd_"):
        cmd_number = data.split("_")[1]
        page_back = "more_1" if int(cmd_number) <= 9 else "more_2"
        await safe_edit_message(
            query,
            f"<b>⚡ You selected Command {cmd_number}</b>\n\n"
            f"Here is the description or usage for command <b>{cmd_number}</b>.",
            InlineKeyboardMarkup(
                [[InlineKeyboardButton("Back", callback_data=page_back),
                  InlineKeyboardButton("Support", url=SUPPORT_LINK)]]
            )
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
