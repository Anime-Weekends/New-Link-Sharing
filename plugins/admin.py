import asyncio
from config import OWNER_ID
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import add_admin, remove_admin, list_admins

# Temporary dict to store user states for adding admin
waiting_for_admin_input = {}

# ── BUTTON HELPERS ──
def main_panel_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Aᴅᴅ ᴀᴅᴍɪɴ", callback_data="add_admin"),
         InlineKeyboardButton("Rᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ", callback_data="remove_admin")],
        [InlineKeyboardButton("◁", callback_data="back_adminpanel"),
         InlineKeyboardButton("✘ Cʟᴏsᴇ", callback_data="close_adminpanel"),
         InlineKeyboardButton("▷", callback_data="extra_panel")]
    ])

def extra_panel_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Aᴅᴍɪɴ ʟɪsᴛ", callback_data="view_admins")],
        [InlineKeyboardButton("◁", callback_data="main_panel"),
         InlineKeyboardButton("✘ Cʟᴏsᴇ", callback_data="close_adminpanel"),
         InlineKeyboardButton("▷", callback_data="extra_panel")]
    ])

def back_close_buttons(back_cb="back_adminpanel"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◁ Bᴀᴄᴋ", callback_data=back_cb),
         InlineKeyboardButton("✘ Cʟᴏsᴇ", callback_data="close_adminpanel")]
    ])

# ── SAFE EDIT ──
async def safe_edit(query: CallbackQuery, new_text: str, reply_markup=None, disable_web_preview=True):
    try:
        if query.message.text != new_text:
            await query.message.edit_text(
                new_text,
                reply_markup=reply_markup,
                disable_web_page_preview=disable_web_preview,
                parse_mode=ParseMode.HTML
            )
        else:
            await query.answer()
    except Exception:
        await query.answer("Uᴘᴅᴀᴛᴇ ғᴀɪʟᴇᴅ", show_alert=True)

# ── MAIN ADMIN PANEL ──
@Client.on_message(filters.command("adminpanel") & filters.user(OWNER_ID))
async def admin_panel_msg(client, message: Message):
    await message.reply_text(
        "≡ 𝗔𝗗𝗠𝗜𝗡 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧 𝗣𝗔𝗡𝗘𝗟\n\n›› ᴛʜɪs ᴘᴀɴᴇʟ ᴀʟʟᴏᴡs ʏᴏᴜ ᴛᴏ sᴇᴀᴍʟᴇssʟʏ ᴀᴅᴅ, ʀᴇᴍᴏᴠᴇ, ᴀɴᴅ ᴠɪᴇᴡ ᴀʟʟ ᴄᴜʀʀᴇɴᴛ ᴀᴅᴍɪɴs.\nㅤ",
        reply_markup=main_panel_buttons()
    )

# ── SWITCH TO EXTRA PANEL ──
@Client.on_callback_query(filters.regex("^extra_panel$"))
async def extra_panel_cb(client, query: CallbackQuery):
    text = (
        "≡ 𝗔𝗗𝗠𝗜𝗡 𝗘𝗫𝗧𝗥𝗔 𝗣𝗔𝗡𝗘𝗟\n\n"
        "›› Hᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴠɪᴇᴡ ᴀᴅᴍɪɴ ʟɪsᴛ ᴀɴᴅ ᴏᴛʜᴇʀ ᴇxᴛʀᴀ ᴏᴩᴛɪᴏɴs.\nㅤ"
    )
    await safe_edit(
        query,
        text,
        reply_markup=extra_panel_buttons()
    )

# ── BACK TO MAIN PANEL ──
@Client.on_callback_query(filters.regex("^main_panel$|^back_adminpanel$"))
async def back_adminpanel(client, query: CallbackQuery):
    await safe_edit(
        query,
        "≡ 𝗔𝗗𝗠𝗜𝗡 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧 𝗣𝗔𝗡𝗘𝗟\n\n›› ᴛʜɪs ᴘᴀɴᴇʟ ᴀʟʟᴏᴡs ʏᴏᴜ ᴛᴏ sᴇᴀᴍʟᴇssʟʏ ᴀᴅᴅ, ʀᴇᴍᴏᴠᴇ, ᴀɴᴅ ᴠɪᴇᴡ ᴀʟʟ ᴄᴜʀʀᴇɴᴛ ᴀᴅᴍɪɴs.\nㅤ",
        reply_markup=main_panel_buttons()
    )

# ── VIEW ADMINS ──
@Client.on_callback_query(filters.regex("^view_admins$"))
async def view_admins_cb(client, query: CallbackQuery):
    admins = await list_admins()
    if not admins:
        text = "<pre>✘ Nᴏ ᴀᴅᴍɪɴs ғᴏᴜɴᴅ</pre>"
    else:
        lines = []
        for uid in admins:
            try:
                user = await client.get_users(uid)
                name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                username = f"@{user.username}" if user.username else "—"
                clickable_id = f"<a href='tg://openmessage?user_id={uid}'>{uid}</a>"
                lines.append(f"<blockquote>›› <b>{name}</b>\n›› {clickable_id}\n›› {username}</blockquote>")
            except Exception:
                lines.append(f"<blockquote>›› Unknown\n›› <a href='tg://openmessage?user_id={uid}'>{uid}</a>\n›› —</blockquote>")
        text = "≡ |  𝗔𝗗𝗠𝗜𝗡 𝗟𝗜𝗦𝗧  |\n\n" + "\n\n".join(lines)

    await safe_edit(query, text, reply_markup=back_close_buttons("extra_panel"))

# ── ADD ADMIN ──
@Client.on_callback_query(filters.regex("^add_admin$"))
async def add_admin_cb(client, query: CallbackQuery):
    await safe_edit(
        query,
        "≡ Sᴇɴᴅ ᴛʜᴇ 𝗨𝗦𝗘𝗥 𝗜𝗗 ᴏғ ᴛʜᴇ ᴜsᴇʀ ᴛᴏ ᴀᴅᴅ ᴀs ᴀᴅᴍɪɴ.\n\n›› 𝟯𝟬s ᴛɪᴍᴇᴏᴜᴛ\nㅤ",
        reply_markup=back_close_buttons()
    )
    waiting_for_admin_input[query.message.chat.id] = query  # store query for editing later

@Client.on_message(filters.text & filters.user(OWNER_ID))
async def handle_add_admin_input(client, message: Message):
    query = waiting_for_admin_input.get(message.chat.id)
    if not query:
        return

    user_input = message.text.strip()
    
    # Delete the UID message immediately
    await message.delete()

    # Typing action
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)

    if not user_input.isdigit():
        await safe_edit(query, "<pre>✘ Iɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ. ᴀᴅᴍɪɴ ɴᴏᴛ ᴀᴅᴅᴇᴅ</pre>", reply_markup=main_panel_buttons())
        waiting_for_admin_input.pop(message.chat.id, None)
        return

    user_id = int(user_input)
    success = await add_admin(user_id)
    status = (f"<pre>✔ Usᴇʀ <code>{user_id}</code> ᴀᴅᴅᴇᴅ ᴀs ᴀᴅᴍɪɴ</pre>" 
              if success else f"<pre>✘ Fᴀɪʟᴇᴅ ᴛᴏ ᴀᴅᴅ <code>{user_id}</code></pre>")

    await safe_edit(query, status, reply_markup=main_panel_buttons())
    waiting_for_admin_input.pop(message.chat.id, None)

# ── REMOVE ADMIN ──
@Client.on_callback_query(filters.regex("^remove_admin$"))
async def remove_admin_cb(client, query: CallbackQuery):
    admins = await list_admins()
    if not admins:
        return await safe_edit(query, "<pre>✘ Nᴏ ᴀᴅᴍɪɴs ᴛᴏ ʀᴇᴍᴏᴠᴇ</pre>", reply_markup=back_close_buttons())

    buttons = [
        [InlineKeyboardButton(f"✘ {uid}", callback_data=f"deladmin_{uid}")]
        for uid in admins
    ]
    buttons.append([
        InlineKeyboardButton("◁ Bᴀᴄᴋ", callback_data="back_adminpanel"),
        InlineKeyboardButton("✘ Cʟᴏsᴇ", callback_data="close_adminpanel")
    ])

    await safe_edit(query, "≡ Sᴇʟᴇᴄᴛ ᴛʜᴇ 𝗨𝗦𝗘𝗥 𝗜𝗗 ᴏғ ᴛʜᴇ ᴜsᴇʀ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴀs ғʀᴏᴍ ᴀᴅᴍɪɴ.\n\n›› 𝟯𝟬s ᴛɪᴍᴇᴏᴜᴛ.\nㅤ", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^deladmin_"))
async def deladmin_cb(client, query: CallbackQuery):
    user_id = int(query.data.split("_")[1])
    
    # Typing action
    await client.send_chat_action(query.message.chat.id, ChatAction.TYPING)

    success = await remove_admin(user_id)
    status = f"<pre>✔ Rᴇᴍᴏᴠᴇᴅ <code>{user_id}</code> ғʀᴏᴍ ᴀᴅᴍɪɴs</pre>" if success else f"<pre>✘ Fᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ <code>{user_id}</code></pre>"

    await safe_edit(query, status, reply_markup=back_close_buttons())

# ── CLOSE PANEL ──
@Client.on_callback_query(filters.regex("^close_adminpanel$"))
async def close_adminpanel(client, query: CallbackQuery):
    try:
        await query.message.delete()
    except:
        await query.answer("✘ Cᴀɴ'ᴛ ᴄʟᴏsᴇ ᴛʜɪs ᴘᴀɴᴇʟ", show_alert=True)
