
import os
import asyncio
from config import *
from pyrogram import Client, filters
from pyrogram.types import Message, User, ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, ChatAdminRequired, RPCError
from database.database import set_approval_off, is_approval_off, add_admin, remove_admin, list_admins

# ── ADMIN PANEL BUTTONS ──
def admin_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 View Admins", callback_data="view_admins")],
        [InlineKeyboardButton("➕ Add Admin", callback_data="add_admin")],
        [InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin")]
    ])

# ── MAIN ADMIN PANEL ──
@Client.on_message(filters.command("adminpanel") & filters.user(OWNER_ID))
async def admin_panel(client, message: Message):
    await message.reply_text(
        "<b>⚙️ Admin Management Panel</b>",
        reply_markup=admin_buttons()
    )

# ── VIEW ADMINS ──
@Client.on_callback_query(filters.regex("^view_admins$"))
async def view_admins_cb(client, query: CallbackQuery):
    admins = await list_admins()
    if not admins:
        text = "❌ No admins found."
    else:
        lines = []
        for uid in admins:
            try:
                user = await client.get_users(uid)
                name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                clickable_id = f"<a href='tg://openmessage?user_id={uid}'>{uid}</a>"
                lines.append(f"Name: {name}\nID: {clickable_id}")
            except Exception:
                lines.append(f"Name: Unknown\nID: <a href='tg://openmessage?user_id={uid}'>{uid}</a>")
        text = "\n\n".join(lines)

    await query.message.edit_text(
        text,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="back_adminpanel")]
        ])
    )

# ── ADD ADMIN ──
@Client.on_callback_query(filters.regex("^add_admin$"))
async def add_admin_cb(client, query: CallbackQuery):
    await query.message.edit_text(
        "✏️ Send me the <b>User ID</b> of the user to add as admin.\n\nℹ️ You have 30s to reply.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Cancel", callback_data="back_adminpanel")]
        ])
    )

    try:
        response: Message = await client.listen(query.message.chat.id, timeout=30)
    except asyncio.TimeoutError:
        return await query.message.edit_text(
            "⌛ Timed out. Returning to admin panel.",
            reply_markup=admin_buttons()
        )

    if not response.text.isdigit():
        return await query.message.edit_text(
            "❌ Invalid User ID. Returning to admin panel.",
            reply_markup=admin_buttons()
        )

    user_id = int(response.text.strip())
    success = await add_admin(user_id)
    status = f"✅ User <code>{user_id}</code> added as admin." if success else f"❌ Failed to add <code>{user_id}</code> as admin."

    await query.message.edit_text(
        status,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="back_adminpanel")]
        ])
    )

# ── REMOVE ADMIN ──
@Client.on_callback_query(filters.regex("^remove_admin$"))
async def remove_admin_cb(client, query: CallbackQuery):
    admins = await list_admins()
    if not admins:
        return await query.message.edit_text(
            "❌ No admins to remove.",
            reply_markup=admin_buttons()
        )

    buttons = [[InlineKeyboardButton(f"❌ {uid}", callback_data=f"deladmin_{uid}")] for uid in admins]
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="back_adminpanel")])

    await query.message.edit_text(
        "👥 Select an admin to remove:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^deladmin_"))
async def deladmin_cb(client, query: CallbackQuery):
    user_id = int(query.data.split("_")[1])
    success = await remove_admin(user_id)
    status = f"✅ Removed <code>{user_id}</code> from admins." if success else f"❌ Failed to remove <code>{user_id}</code>."

    await query.message.edit_text(
        status,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="back_adminpanel")]
        ])
    )

# ── BACK TO PANEL ──
@Client.on_callback_query(filters.regex("^back_adminpanel$"))
async def back_adminpanel(client, query: CallbackQuery):
    await query.message.edit_text(
        "<b><blockquote>⚙️ Admin Management Panel</b></blockquote>",
        reply_markup=admin_buttons()
)
