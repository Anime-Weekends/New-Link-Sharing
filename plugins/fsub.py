import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated
from database.database import (
    add_channel,
    del_channel,
    show_channels,
    get_channel_mode,
    reqChannel_exist,
    req_user,
    req_user_exist,
    del_req_user,
    rqst_fsub_Channel_data
)
from config import OWNER_ID


# ========================= FORCE-SUB MODE ========================= #

@Client.on_message(filters.command('fsub_mode') & filters.private & filters.user(OWNER_ID))
async def change_force_sub_mode(client: Client, message: Message):
    temp = await message.reply("<b><i>Wait a sec...</i></b>", quote=True)
    channels = await show_channels()

    if not channels:
        return await temp.edit("<b>❌ No force-sub channels found.</b>")

    buttons = []
    for ch in channels:
        ch_id = ch["_id"] if isinstance(ch, dict) else ch
        try:
            chat = await client.get_chat(ch_id)
            mode = await get_channel_mode(ch_id)
            status = "🟢" if mode == "on" else "🔴"
            title = f"{status} {chat.title}"
            buttons.append([InlineKeyboardButton(title, callback_data=f"rfs_ch_{ch_id}")])
        except:
            buttons.append([InlineKeyboardButton(f"⚠️ {ch_id} (Unavailable)", callback_data=f"rfs_ch_{ch_id}")])

    buttons.append([InlineKeyboardButton("Close ✖️", callback_data="close")])
    await temp.edit(
        "<b>⚡ Select a channel to toggle Force-Sub Mode:</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )


# ========================= MEMBERSHIP HANDLERS ========================= #

@Client.on_chat_member_updated()
async def handle_chat_members(client, chat_member_updated: ChatMemberUpdated):
    chat_id = chat_member_updated.chat.id
    if await reqChannel_exist(chat_id):
        old_member = chat_member_updated.old_chat_member
        if old_member and old_member.status == ChatMemberStatus.MEMBER:
            user_id = old_member.user.id
            if await req_user_exist(chat_id, user_id):
                await del_req_user(chat_id, user_id)


@Client.on_chat_join_request()
async def handle_join_request(client, chat_join_request):
    chat_id = chat_join_request.chat.id
    user_id = chat_join_request.from_user.id
    if await reqChannel_exist(chat_id):
        if not await req_user_exist(chat_id, user_id):
            await req_user(chat_id, user_id)


# ========================= CHANNEL MANAGEMENT ========================= #

@Client.on_message(filters.command('addchnl') & filters.private & filters.user(OWNER_ID))
async def add_force_sub(client: Client, message: Message):
    temp = await message.reply("Wait a sec...", quote=True)
    args = message.text.split(maxsplit=1)

    if len(args) != 2:
        return await temp.edit("Usage:\n<code>/addchnl -100xxxxxxxxxx</code>")

    try:
        chat_id = int(args[1])
    except ValueError:
        return await temp.edit("❌ Invalid chat ID!")

    all_chats = await show_channels()
    if chat_id in [c if isinstance(c, int) else c["_id"] for c in all_chats]:
        return await temp.edit(f"Already exists:\n<code>{chat_id}</code>")

    try:
        chat = await client.get_chat(chat_id)
        if chat.type not in [ChatType.CHANNEL, ChatType.SUPERGROUP]:
            return await temp.edit("❌ Only channels/supergroups allowed.")

        bot_member = await client.get_chat_member(chat.id, "me")
        if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await temp.edit("❌ Bot must be admin in that chat.")

        try:
            link = await client.export_chat_invite_link(chat.id)
        except Exception:
            link = f"https://t.me/{chat.username}" if chat.username else f"https://t.me/c/{str(chat.id)[4:]}"

        await add_channel(chat_id)
        await temp.edit(
            f"✅ Added Successfully!\n\n"
            f"<b>Name:</b> <a href='{link}'>{chat.title}</a>\n"
            f"<b>ID:</b> <code>{chat_id}</code>",
            disable_web_page_preview=True
        )
    except Exception as e:
        await temp.edit(f"❌ Failed to add chat:\n<code>{chat_id}</code>\n\n<i>{e}</i>")


@Client.on_message(filters.command('delchnl') & filters.private & filters.user(OWNER_ID))
async def del_force_sub(client: Client, message: Message):
    temp = await message.reply("<b><i>Wait a sec...</i></b>", quote=True)
    args = message.text.split(maxsplit=1)
    all_channels = await show_channels()

    if len(args) != 2:
        return await temp.edit("<b>Usage:</b> <code>/delchnl <channel_id | all></code>")

    if args[1].lower() == "all":
        if not all_channels:
            return await temp.edit("<b>❌ No force-sub channels found.</b>")
        for ch_id in all_channels:
            ch_id_val = ch_id["_id"] if isinstance(ch_id, dict) else ch_id
            await del_channel(ch_id_val)
        return await temp.edit("<b>✅ All force-sub channels have been removed.</b>")

    try:
        ch_id = int(args[1])
    except ValueError:
        return await temp.edit("<b>❌ Invalid Channel ID</b>")

    if ch_id in [c["_id"] if isinstance(c, dict) else c for c in all_channels]:
        await del_channel(ch_id)
        await temp.edit(f"<b>✅ Channel removed:</b> <code>{ch_id}</code>")
    else:
        await temp.edit(f"<b>❌ Channel not found in force-sub list:</b> <code>{ch_id}</code>")


@Client.on_message(filters.command('listchnl') & filters.private & filters.user(OWNER_ID))
async def list_force_sub_channels(client: Client, message: Message):
    temp = await message.reply("<b><i>Wait a sec...</i></b>", quote=True)
    channels = await show_channels()

    if not channels:
        return await temp.edit("<b>❌ No force-sub channels found.</b>")

    result = "<b>⚡ Force-sub Channels:</b>\n\n"
    for ch in channels:
        ch_id = ch["_id"] if isinstance(ch, dict) else ch
        try:
            chat = await client.get_chat(ch_id)
            link = chat.invite_link or await client.export_chat_invite_link(chat.id)
            result += f"<b>•</b> <a href='{link}'>{chat.title}</a> [<code>{ch_id}</code>]\n"
        except Exception:
            result += f"<b>•</b> <code>{ch_id}</code> — <i>Unavailable</i>\n"

    await temp.edit(result, disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Close ✖️", callback_data="close")]]))


@Client.on_message(filters.command('delreq') & filters.private & filters.user(OWNER_ID))
async def delete_requested_users(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Usage: /delreq <channel_id>", quote=True)

    try:
        channel_id = int(message.command[1])
    except ValueError:
        return await message.reply("❌ Invalid channel ID.", quote=True)

    channel_data = await rqst_fsub_Channel_data.find_one({'_id': channel_id})
    if not channel_data:
        return await message.reply("ℹ️ No request channel found for this channel.", quote=True)

    user_ids = channel_data.get("user_ids", [])
    if not user_ids:
        return await message.reply("✅ No users to process.", quote=True)

    removed = 0
    skipped = 0
    left_users = 0

    for user_id in user_ids:
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                skipped += 1
                continue
            else:
                await del_req_user(channel_id, user_id)
                left_users += 1
        except:
            await del_req_user(channel_id, user_id)
            left_users += 1

    for user_id in user_ids:
        if not await req_user_exist(channel_id, user_id):
            await del_req_user(channel_id, user_id)
            removed += 1

    await message.reply(
        f"✅ Cleanup completed for channel `{channel_id}`\n\n"
        f"👤 Removed users not in channel: `{left_users}`\n"
        f"🗑️ Removed leftover non-request users: `{removed}`\n"
        f"✅ Still members: `{skipped}`",
        quote=True
)
