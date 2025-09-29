import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatMemberUpdated
)
from config import OWNER_ID
from database.database import (
    save_channel,
    delete_channel,
    get_channels,
    add_fsub_channel,
    remove_fsub_channel,
    get_fsub_channels,
)

# ========================= FORCE-SUB MODE ========================= #

@Client.on_message(filters.command('fsub_mode') & filters.private & filters.user(OWNER_ID))
async def change_force_sub_mode(client: Client, message: Message):
    temp = await message.reply("<b><i>Wait a sec...</i></b>", quote=True)
    channels = await get_fsub_channels()

    if not channels:
        return await temp.edit("<b>❌ No force-sub channels found.</b>")

    buttons = []
    for ch_id in channels:
        try:
            chat = await client.get_chat(ch_id)
            # no mode system in your db, just show active
            title = f"🟢 {chat.title}"
            buttons.append([InlineKeyboardButton(title, callback_data=f"rfs_ch_{ch_id}")])
        except:
            buttons.append([InlineKeyboardButton(f"⚠️ {ch_id} (Unavailable)", callback_data=f"rfs_ch_{ch_id}")])

    buttons.append([InlineKeyboardButton("Close ✖️", callback_data="close")])
    await temp.edit(
        "<b>⚡ Force-sub Channels:</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )

# ========================= MEMBERSHIP HANDLERS ========================= #

@Client.on_chat_member_updated()
async def handle_chat_members(client, chat_member_updated: ChatMemberUpdated):
    # Here you can extend if you track users per channel in db
    pass

@Client.on_chat_join_request()
async def handle_join_request(client, chat_join_request):
    # Same here, extend if you store user join-requests in db
    pass

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

    existing = await get_fsub_channels()
    if chat_id in existing:
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

        await add_fsub_channel(chat_id)
        await save_channel(chat_id)
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
    all_channels = await get_fsub_channels()

    if len(args) != 2:
        return await temp.edit("<b>Usage:</b> <code>/delchnl <channel_id | all></code>")

    if args[1].lower() == "all":
        if not all_channels:
            return await temp.edit("<b>❌ No force-sub channels found.</b>")
        for ch_id in all_channels:
            await remove_fsub_channel(ch_id)
            await delete_channel(ch_id)
        return await temp.edit("<b>✅ All force-sub channels have been removed.</b>")

    try:
        ch_id = int(args[1])
    except ValueError:
        return await temp.edit("<b>❌ Invalid Channel ID</b>")

    if ch_id in all_channels:
        await remove_fsub_channel(ch_id)
        await delete_channel(ch_id)
        await temp.edit(f"<b>✅ Channel removed:</b> <code>{ch_id}</code>")
    else:
        await temp.edit(f"<b>❌ Channel not found in force-sub list:</b> <code>{ch_id}</code>")

@Client.on_message(filters.command('listchnl') & filters.private & filters.user(OWNER_ID))
async def list_force_sub_channels(client: Client, message: Message):
    temp = await message.reply("<b><i>Wait a sec...</i></b>", quote=True)
    channels = await get_fsub_channels()

    if not channels:
        return await temp.edit("<b>❌ No force-sub channels found.</b>")

    result = "<b>⚡ Force-sub Channels:</b>\n\n"
    for ch_id in channels:
        try:
            chat = await client.get_chat(ch_id)
            link = chat.invite_link or await client.export_chat_invite_link(chat.id)
            result += f"<b>•</b> <a href='{link}'>{chat.title}</a> [<code>{ch_id}</code>]\n"
        except Exception:
            result += f"<b>•</b> <code>{ch_id}</code> — <i>Unavailable</i>\n"

    await temp.edit(
        result,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Close ✖️", callback_data="close")]])
    )
