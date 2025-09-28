# +++ Modified By Yato [telegram username: @i_killed_my_clan & @ProYato] +++ # aNDI BANDI SANDI JISNE BHI CREDIT HATAYA USKI BANDI RAndi 
import asyncio
import base64
import time
from collections import defaultdict
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.errors import FloodWait, UserNotParticipant

from bot import Bot
from datetime import datetime, timedelta
from config import *
from database.database import *
from plugins.newpost import revoke_invite_after_5_minutes
from helper_func import *


user_banned_until = {}

# Broadcast variables
cancel_lock = asyncio.Lock()
is_canceled = False

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
# 
    # Check FSub requirements
   #  fsub_channels = await get_fsub_channels()
   #  if fsub_channels:
    #     is_subscribed, subscription_message, subscription_buttons = await check_subscription_status(client, user_id, fsub_channels)
   #      if not is_subscribed:
    #         return await message.reply_text(
    #             subscription_message,
    #             reply_markup=subscription_buttons,
    #             parse_mode=ParseMode.HTML
     #        )

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


#=====================================================================================##
# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport

#=====================================================================================##


@Bot.on_callback_query(filters.regex("close"))
async def close_callback(client: Bot, callback_query):
    await callback_query.answer()
    await callback_query.message.delete()

@Bot.on_callback_query(filters.regex("check_sub"))
async def check_sub_callback(client: Bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    fsub_channels = await get_fsub_channels()
    
    if not fsub_channels:
        await callback_query.message.edit_text(
            "<b>No FSub channels configured!</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    is_subscribed, subscription_message, subscription_buttons = await check_subscription_status(client, user_id, fsub_channels)
    if is_subscribed:
        await callback_query.message.edit_text(
            "<b>You are subscribed to all required channels! Use /start to proceed.</b>",
            parse_mode=ParseMode.HTML
        )
    else:
        await callback_query.message.edit_text(
            subscription_message,
            reply_markup=subscription_buttons,
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
    now = datetime.now()
    delta = now - client.uptime
    bottime = get_readable_time(delta.seconds)
    
    await temp_msg.edit(
        f"<b>Users: {len(users)}\n\nUptime: {bottime}\n\nPing: {ping_time:.2f} ms</b>",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )




@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    if data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    elif data in ["about", "channels"]:
        # Show a simple "progress" animation
        try:
            await query.message.edit_text("● ◌ ◌")
            await asyncio.sleep(0.3)
            await query.message.edit_text("● ● ◌")
            await asyncio.sleep(0.3)
            await query.message.edit_text("● ● ●")
            await asyncio.sleep(0.2)
        except:
            pass  # In case message was deleted or can't edit

        # Show the actual content
        if data == "about":
            user = await client.get_users(OWNER_ID)
            user_link = f"https://t.me/{user.username}" if user.username else f"tg://openmessage?user_id={OWNER_ID}"

            await query.edit_message_media(
                media=InputMediaPhoto(
                    media="https://envs.sh/Wdj.jpg",
                    caption=ABOUT_TXT
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('• ʙᴀᴄᴋ', callback_data='start'),
                     InlineKeyboardButton('ᴄʟᴏsᴇ •', callback_data='close')]
                ])
            )
            await query.edit_message_caption(
                caption=ABOUT_TXT,
                parse_mode=ParseMode.HTML
            )

        else:  # channels
            user = await client.get_users(OWNER_ID)
            user_link = f"https://t.me/{user.username}" if user.username else f"tg://openmessage?user_id={OWNER_ID}"
            ownername = f"<a href={user_link}>{user.first_name}</a>" if user.first_name else f"<a href={user_link}>no name !</a>"

            await query.edit_message_media(
                media=InputMediaPhoto(
                    media="https://envs.sh/Wdj.jpg",
                    caption=CHANNELS_TXT
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('• ʙᴀᴄᴋ', callback_data='start'),
                     InlineKeyboardButton('home•', callback_data='setting')]
                ])
            )
            await query.edit_message_caption(
                caption=CHANNELS_TXT,
                parse_mode=ParseMode.HTML
            )

    elif data in ["start", "home"]:
        inline_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="about"),
             InlineKeyboardButton("• ᴄʜᴀɴɴᴇʟs", callback_data="channels")],
            [InlineKeyboardButton("• Close •", callback_data="close")]
        ])
        try:
            await query.edit_message_media(
                media=InputMediaPhoto(
                    media=START_PIC,
                    caption=START_MSG
                ),
                reply_markup=inline_buttons
            )
            await query.edit_message_caption(
                caption=START_MSG,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            print(f"Error sending start/home photo: {e}")
            await query.edit_message_text(
                text=START_MSG,
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
