# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
#     ✧ R ᴇ x ʏ   -   レクシィ   -   Dᴇᴠ ✧
# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦

import asyncio
from datetime import datetime, timedelta
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
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
cancel_lock = asyncio.Lock()
is_canceled = False
WAIT_MSG = "<b>Processing...</b>"
REPLY_ERROR = "<code>Use this command as a reply to any Telegram message without any spaces.</code>"

# ---------------- Admin filter (uses ADMINS from config.py) ---------------- #
# Wrap as a pyrogram custom filter so it can be used in decorators
def _owner_filter(_, __, message: Message):
    return bool(message.from_user and message.from_user.id in ADMINS)

is_owner_or_admin = filters.create(_owner_filter)

# ========================= START COMMAND ========================= #
@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Bot, message: Message):
    user_id = message.from_user.id
    now = datetime.now()

    # If temporarily banned, notify and return
    if user_id in user_banned_until and now < user_banned_until[user_id]:
        await message.reply_text(
            "<b><blockquote expandable>You are temporarily banned from using commands due to spamming. Try again later.</b>",
            parse_mode=ParseMode.HTML
        )
        return

    # Add user record (assumes add_user exists in database.database)
    try:
        await add_user(user_id)
    except Exception:
        # don't break start if DB add fails
        pass

    # If bot was started with an encoded link payload
    text = message.text or ""
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
                await message.reply_text(
                    "<b><blockquote expandable>Invalid or expired invite link.</b>",
                    parse_mode=ParseMode.HTML
                )
                return

            # If an original link exists, show it directly
            try:
                original_link = await get_original_link(channel_id)
            except Exception:
                original_link = None

            if original_link:
                btn = InlineKeyboardMarkup([[InlineKeyboardButton("• Proceed to Link •", url=original_link)]])
                await message.reply_text(
                    "<b><blockquote expandable>Here is your link! Click below to proceed</b>",
                    reply_markup=btn,
                    parse_mode=ParseMode.HTML
                )
                return

            # revoke previous invite if present
            old_link_info = await get_current_invite_link(channel_id)
            if old_link_info:
                try:
                    await client.revoke_chat_invite_link(channel_id, old_link_info["invite_link"])
                except Exception:
                    pass

            # create new invite for 5 minutes
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
            try:
                await wait_msg.delete()
            except Exception:
                pass

            await message.reply_text(
                "<b><blockquote expandable>Here is your link! Click below to proceed</b>",
                reply_markup=button,
                parse_mode=ParseMode.HTML
            )

            note_msg = await message.reply_text(
                "<u><b>Note: If the link is expired, click the post link again to get a new one.</b></u>",
                parse_mode=ParseMode.HTML
            )
            delete_after_delay(note_msg, 300)
            asyncio.create_task(revoke_invite_after_5_minutes(client, channel_id, invite.invite_link, is_request))

        except Exception as e:
            # Generic fallback message
            await message.reply_text(
                "<b><blockquote expandable>Invalid or expired invite link.</b>",
                parse_mode=ParseMode.HTML
            )
            # keep a lightweight log
            try:
                print(f"[start_command] decoding error: {e}")
            except:
                pass

    else:
        # Normal start message with inline keyboard
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
        except Exception:
            # fallback to text if sending photo fails
            await message.reply_text(
                START_MSG,
                reply_markup=inline_buttons,
                parse_mode=ParseMode.HTML
            )

# ========================= CALLBACK HANDLERS ========================= #
@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = (query.data or "").strip()
    # answer callback quickly so Telegram doesn't complain
    try:
        await query.answer()
    except:
        pass

    # ----- Close: delete UI ----- #
    if data == "close":
        try:
            await query.message.delete()
        except:
            pass
        return

    # ----- About / Channels: show animation then final content ----- #
    if data in ("about", "channels"):
        # animation loop (safe)
        try:
            for i in range(1, 4):
                # e.g. "● ○ ○", "● ● ○", "● ● ●"
                dots = " ".join(["●"] * i + ["○"] * (3 - i))
                # use edit_text for the animation (works for media or text messages)
                try:
                    await query.message.edit_text(dots)
                except:
                    # some messages may not allow edit_text (rare), ignore and continue
                    pass
                await asyncio.sleep(0.28)
        except Exception:
            # do not abort on animation failure
            pass

        # small pause to make animation feel finished
        await asyncio.sleep(0.12)

        caption = ABOUT_TXT if data == "about" else CHANNELS_TXT
        inline_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton('• Back', callback_data='start'),
             InlineKeyboardButton('• Close', callback_data='close')]
        ])

        # If original message currently contains media (photo/video/document), prefer edit_media
        has_media = bool(getattr(query.message, "photo", None) or getattr(query.message, "video", None) or getattr(query.message, "document", None))

        if has_media:
            try:
                await query.message.edit_media(
                    media=InputMediaPhoto(media="https://envs.sh/Wdj.jpg", caption=caption),
                    reply_markup=inline_buttons
                )
            except Exception:
                # fallback to edit_text if edit_media fails
                try:
                    await query.message.edit_text(text=caption, reply_markup=inline_buttons, parse_mode=ParseMode.HTML)
                except:
                    pass
        else:
            try:
                await query.message.edit_text(text=caption, reply_markup=inline_buttons, parse_mode=ParseMode.HTML)
            except Exception:
                # final fallback: try edit_media (if the message can be converted)
                try:
                    await query.message.edit_media(
                        media=InputMediaPhoto(media="https://envs.sh/Wdj.jpg", caption=caption),
                        reply_markup=inline_buttons
                    )
                except:
                    pass
        return

    # ----- Start / Home: show start UI ----- #
    if data in ("start", "home"):
        inline_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("• About", callback_data="about"),
             InlineKeyboardButton("• Channels", callback_data="channels")],
            [InlineKeyboardButton("• Close •", callback_data="close")]
        ])
        # prefer edit_media for nicer look, fallback to edit_text
        try:
            await query.message.edit_media(
                media=InputMediaPhoto(media=START_PIC, caption=START_MSG),
                reply_markup=inline_buttons
            )
        except Exception:
            try:
                await query.message.edit_text(text=START_MSG, reply_markup=inline_buttons, parse_mode=ParseMode.HTML)
            except:
                pass
        return

# ========================= SPAM MONITOR ========================= #
MAX_MESSAGES = 3
TIME_WINDOW = timedelta(seconds=10)
BAN_DURATION = timedelta(hours=1)

@Bot.on_message(filters.private)
async def monitor_spam(client: Bot, message: Message):
    user_id = message.from_user.id
    now = datetime.now()

    # ignore commands (so /start etc are not counted)
    if message.text and message.text.startswith("/"):
        return

    # admins bypass the spam monitor
    try:
        if user_id in ADMINS:
            return
    except Exception:
        # if ADMINS isn't defined for some reason, don't crash
        pass

    # if currently banned, notify
    if user_id in user_banned_until and now < user_banned_until[user_id]:
        await message.reply_text(
            "<b>You are temporarily banned from sending messages due to spam. Try later.</b>",
            parse_mode=ParseMode.HTML
        )
        return

    # initialize list and append timestamp
    if user_id not in user_message_count:
        user_message_count[user_id] = []
    user_message_count[user_id].append(now)

    # keep only timestamps inside the window
    user_message_count[user_id] = [t for t in user_message_count[user_id] if now - t <= TIME_WINDOW]

    # if exceeded threshold -> ban
    if len(user_message_count[user_id]) > MAX_MESSAGES:
        user_banned_until[user_id] = now + BAN_DURATION
        # clear stored timestamps to avoid immediate rebans after ban expiration
        user_message_count[user_id] = []
        await message.reply_text(
            "<b>You are temporarily banned from sending messages due to spam. Try later.</b>",
            parse_mode=ParseMode.HTML
        )

# ========================= UTILITIES ========================= #
def delete_after_delay(msg, delay: int):
    """
    Schedules deletion of a message after `delay` seconds.
    Call without await: delete_after_delay(msg, 300)
    """
    async def _inner():
        await asyncio.sleep(delay)
        try:
            await msg.delete()
        except Exception:
            pass
    # schedule, don't await
    try:
        asyncio.create_task(_inner())
    except RuntimeError:
        # if event loop isn't running yet, ignore (safe fallback)
        pass
