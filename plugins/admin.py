
import os
import asyncio
from config import *
from pyrogram import Client, filters
from pyrogram.types import Message, User, ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, ChatAdminRequired, RPCError
from database.database import set_approval_off, is_approval_off, add_admin, remove_admin, list_admins


# ── ADMIN MENU ──

@Client.on_message(filters.command("adminpanel") & filters.user(OWNER_ID))
async def admin_panel(client, message: Message):
    buttons = [
        [InlineKeyboardButton("👥 View Admins", callback_data="view_admins")],
        [InlineKeyboardButton("➕ Add Admin", callback_data="add_admin")],
        [InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin")]
    ]
    await message.reply_text(
        "⚙️ <b>Admin Management Panel</b>",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ── VIEW ADMINS ──

@Client.on_callback_query(filters.regex("^view_admins$"))
async def view_admins_cb(client, query: CallbackQuery):
    admins = await list_admins()
    if not admins:
        text = "❌ No admins found."
    else:
        text = "<b>Admin User IDs:</b>\n" + "\n".join([f"<code>{uid}</code>" for uid in admins])

    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="back_adminpanel")]
        ])
    )


# ── ADD ADMIN ──

@Client.on_callback_query(filters.regex("^add_admin$"))
async def add_admin_cb(client, query: CallbackQuery):
    await query.message.edit_text(
        "✏️ Send me the <b>User ID</b> of the user you want to add as admin.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Cancel", callback_data="back_adminpanel")]
        ])
    )
    # Wait for the next message
    response: Message = await client.listen(query.message.chat.id)
    if not response.text.isdigit():
        return await query.message.reply_text("❌ Invalid User ID. Please try again.")

    user_id = int(response.text)
    success = await add_admin(user_id)
    if success:
        await query.message.reply_text(f"✅ User <code>{user_id}</code> added as admin.")
    else:
        await query.message.reply_text(f"❌ Failed to add <code>{user_id}</code> as admin.")


# ── REMOVE ADMIN ──

@Client.on_callback_query(filters.regex("^remove_admin$"))
async def remove_admin_cb(client, query: CallbackQuery):
    admins = await list_admins()
    if not admins:
        return await query.message.edit_text("❌ No admins to remove.")

    buttons = [[InlineKeyboardButton(f"❌ {uid}", callback_data=f"deladmin_{uid}")]
               for uid in admins]
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="back_adminpanel")])

    await query.message.edit_text(
        "👥 Select an admin to remove:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^deladmin_"))
async def deladmin_cb(client, query: CallbackQuery):
    user_id = int(query.data.split("_")[1])
    success = await remove_admin(user_id)
    if success:
        await query.answer(f"✅ Removed {user_id} from admins.")
    else:
        await query.answer(f"❌ Failed to remove {user_id}.")
    await remove_admin_cb(client, query)


# ── BACK TO MENU ──
@Client.on_callback_query(filters.regex("^back_adminpanel$"))
async def back_adminpanel(client, query: CallbackQuery):
    await admin_panel(client, query.message)
