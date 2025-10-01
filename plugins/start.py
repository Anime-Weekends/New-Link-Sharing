import asyncio
import base64
from datetime import datetime, timedelta
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    InputMediaPhoto
)

from config import *
from bot import Bot
from database.database import (
    add_user,
    get_channel_by_encoded_link,
    get_channel_by_encoded_link2,
    get_original_link,
    get_current_invite_link,
    save_invite_link,
    get_fsub_channels
)
from plugins.newpost import revoke_invite_after_5_minutes
from helper_func import *
from bot import Bot  # <-- import your Bot class

# ========================= GLOBALS ========================= #
user_message_count = {}
user_banned_until = {}
WAIT_MSG = "<b>Processing...</b>"

MAX_MESSAGES = 3
TIME_WINDOW = timedelta(seconds=10)
BAN_DURATION = timedelta(hours=1)

# ========================= START COMMAND ========================= #
@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Bot, message: Message):
    user_id = message.from_user.id
    now = datetime.now()

    # Anti-spam temporary ban check
    if user_id in user_banned_until and now < user_banned_until[user_id]:
        return await message.reply_text(
            "<b>You are temporarily banned from using commands due to spamming. Try again later.</b>",
            parse_mode=ParseMode.HTML
        )

    await add_user(user_id)

    # ================== FORCE-SUB CHECK ================== #
    fsub_channels = await get_fsub_channels()
    if fsub_channels:
        not_joined = []
        for ch_id in fsub_channels:
            try:
                member = await client.get_chat_member(ch_id, user_id)
                if member.status not in [
                    ChatMemberStatus.MEMBER,
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.OWNER
                ]:
                    not_joined.append(ch_id)
            except:
                not_joined.append(ch_id)

        if not_joined:
            buttons = []
            for ch_id in not_joined:
                try:
                    chat = await client.get_chat(ch_id)
                    if chat.username:
                        url = f"https://t.me/{chat.username}"
                    else:
                        url = f"https://t.me/c/{str(chat.id)[4:]}"
                    buttons.append([InlineKeyboardButton(chat.title, url=url)])
                except:
                    buttons.append([InlineKeyboardButton(str(ch_id), url=f"https://t.me/c/{str(ch_id)[4:]}")])
            buttons.append([InlineKeyboardButton("✅ I Joined", callback_data="refresh_start")])

            return await message.reply_text(
                "<b>🚨 You must join the required channel(s) before using me.</b>",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.HTML
            )

    # ================== START LOGIC ================== #
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
                    "<b>Invalid or expired invite link.</b>",
                    parse_mode=ParseMode.HTML
                )

            original_link = await get_original_link(channel_id)
            if original_link:
                button = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("• Proceed to Link •", url=original_link)]]
                )
                return await message.reply_text(
                    "<b>Here is your link! Click below to proceed</b>",
                    reply_markup=button,
                    parse_mode=ParseMode.HTML
                )

            old_link_info = await get_current_invite_link(channel_id)
            if old_link_info:
                try:
                    await client.revoke_chat_invite_link(channel_id, old_link_info["invite_link"])
                except:
                    pass

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
                "<b>Here is your link! Click below to proceed</b>",
                reply_markup=button,
                parse_mode=ParseMode.HTML
            )

            note_msg = await message.reply_text(
                "<b>Note: If the link is expired, click the post link again to get a new one.</b>",
                parse_mode=ParseMode.HTML
            )
            delete_after_delay(note_msg, 300)
            asyncio.create_task(
                revoke_invite_after_5_minutes(client, channel_id, invite.invite_link, is_request)
            )

        except Exception as e:
            await message.reply_text(
                "<b>Invalid or expired invite link.</b>",
                parse_mode=ParseMode.HTML
            )
            print(f"Decoding error: {e}")

    else:
        inline_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("• About", callback_data="about"),
             InlineKeyboardButton("• Channels", callback_data="channels")],
            [InlineKeyboardButton("• Close •", callback_data="close")]
        ])
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

# ========================= CALLBACK HANDLER ========================= #
@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    if data == "close":
        await query.answer()
        try:
            await query.message.delete()
        except:
            pass
        return

    elif data in ["about", "channels"]:
        buttons = [
            [InlineKeyboardButton('• Back', callback_data='start'),
             InlineKeyboardButton('• Close •', callback_data='close')]
        ]

        try:
            for i in range(1, 4):
                dots = "● " * i + "○ " * (3 - i)
                await query.message.edit_text(text=dots)
                await asyncio.sleep(0.3)
        except:
            pass

        caption = ABOUT_TXT if data == "about" else CHANNELS_TXT
        try:
            await client.edit_message_media(
                chat_id=query.message.chat.id,
                message_id=query.message.id,
                media=InputMediaPhoto(
                    media="https://envs.sh/Wdj.jpg",
                    caption=caption
                ),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except:
            await query.message.edit_text(
                text=caption,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.HTML
            )

    elif data in ["start", "home", "refresh_start"]:
        buttons = [
            [InlineKeyboardButton("• About", callback_data="about"),
             InlineKeyboardButton("• Channels", callback_data="channels")],
            [InlineKeyboardButton("• Close •", callback_data="close")]
        ]
        try:
            await client.edit_message_media(
                chat_id=query.message.chat.id,
                message_id=query.message.id,
                media=InputMediaPhoto(
                    media=START_PIC,
                    caption=START_MSG
                ),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except:
            await query.message.edit_text(
                text=START_MSG,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.HTML
            )

# ========================= SPAM MONITOR ========================= #
@Bot.on_message(filters.private)
async def monitor_messages(client: Bot, message: Message):
    user_id = message.from_user.id
    now = datetime.now()

    if message.text and message.text.startswith("/"):
        return
    if user_id in ADMINS:
        return
    if user_id in user_banned_until and now < user_banned_until[user_id]:
        await message.reply_text(
            "<b>You are temporarily banned from sending messages due to spam. Try later.</b>",
            parse_mode=ParseMode.HTML
        )
        return

    if user_id not in user_message_count:
        user_message_count[user_id] = []
    user_message_count[user_id].append(now)
    user_message_count[user_id] = [t for t in user_message_count[user_id] if now - t <= TIME_WINDOW]

    if len(user_message_count[user_id]) > MAX_MESSAGES:
        user_banned_until[user_id] = now + BAN_DURATION
        await message.reply_text(
            "<b>You are temporarily banned from sending messages due to spam. Try later.</b>",
            parse_mode=ParseMode.HTML
        )

# ========================= UTILITY ========================= #
def delete_after_delay(msg, delay):
    async def inner():
        await asyncio.sleep(delay)
        try:
            await msg.delete()
        except:
            pass
    asyncio.create_task(inner())
