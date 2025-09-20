import asyncio
from config import OWNER_ID
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import add_admin, remove_admin, list_admins


# ── BUTTON SETUPS ──
def main_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
            InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin")
        ],
        [
            InlineKeyboardButton("⬅️", callback_data="back_adminpanel"),
            InlineKeyboardButton("❌ Close", callback_data="close_panel"),
            InlineKeyboardButton("➡️", callback_data="view_admins")
        ]
    ])


def back_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬅️", callback_data="back_adminpanel"),
            InlineKeyboardButton("❌ Close", callback_data="close_panel"),
            InlineKeyboardButton("➡️", callback_data="view_admins")
        ]
    ])


# ── SAFE EDIT HELPER ──
async def safe_edit(query: CallbackQuery, new_text: str, reply_markup=None, disable_web_preview=False):
    if query.message.text != new_text:
        await query.message.edit_text(
            new_text,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_preview
        )
    else:
        await query.answer()  # silently acknowledge


# ── MAIN PANEL ──
@Client.on_message(filters.command("adminpanel") & filters.user(OWNER_ID))
async def admin_panel_msg(client, message: Message):
    await message.reply_text(
        "<b>⚙️ Admin Management Panel</b>",
        reply_markup=main_buttons()
    )


# ── VIEW ADMINS (➡️) ──
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
                uname = f"@{user.username}" if user.username else "(no username)"
                lines.append(f"👤 <b>{name}</b>\n🆔 {clickable_id}\n🌐 {uname}")
            except Exception:
                lines.append(f"👤 Unknown\n🆔 <a href='tg://openmessage?user_id={uid}'>{uid}</a>")
        text = "<b>👥 Admin List</b>\n\n" + "\n\n".join(lines)

    await safe_edit(query, text, reply_markup=back_buttons(), disable_web_preview=True)


# ── ADD ADMIN ──
@Client.on_callback_query(filters.regex("^add_admin$"))
async def add_admin_cb(client, query: CallbackQuery):
    await safe_edit(
        query,
        "✏️ Send me the <b>User ID</b> to add as admin.\n\n⏳ You have 30s.",
        reply_markup=back_buttons()
    )

    try:
        response: Message = await client.listen(query.message.chat.id, timeout=30)
    except asyncio.TimeoutError:
        return await safe_edit(query, "⌛ Timed out.", reply_markup=main_buttons())

    if not response.text.isdigit():
        return await safe_edit(query, "❌ Invalid User ID.", reply_markup=main_buttons())

    user_id = int(response.text.strip())
    success = await add_admin(user_id)
    status = f"✅ Added <code>{user_id}</code> as admin." if success else f"❌ Failed to add <code>{user_id}</code>."

    await safe_edit(query, status, reply_markup=back_buttons())


# ── REMOVE ADMIN ──
@Client.on_callback_query(filters.regex("^remove_admin$"))
async def remove_admin_cb(client, query: CallbackQuery):
    admins = await list_admins()
    if not admins:
        return await safe_edit(query, "❌ No admins to remove.", reply_markup=back_buttons())

    buttons = [[InlineKeyboardButton(f"❌ {uid}", callback_data=f"deladmin_{uid}")] for uid in admins]
    buttons.append([
        InlineKeyboardButton("⬅️", callback_data="back_adminpanel"),
        InlineKeyboardButton("❌ Close", callback_data="close_panel"),
        InlineKeyboardButton("➡️", callback_data="view_admins")
    ])

    await safe_edit(query, "👥 Select an admin to remove:", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^deladmin_"))
async def deladmin_cb(client, query: CallbackQuery):
    user_id = int(query.data.split("_")[1])
    success = await remove_admin(user_id)
    status = f"✅ Removed <code>{user_id}</code>." if success else f"❌ Failed to remove <code>{user_id}</code>."

    await safe_edit(query, status, reply_markup=back_buttons())


# ── BACK (⬅️) ──
@Client.on_callback_query(filters.regex("^back_adminpanel$"))
async def back_adminpanel(client, query: CallbackQuery):
    await safe_edit(query, "<b>⚙️ Admin Management Panel</b>", reply_markup=main_buttons())


# ── CLOSE PANEL (❌) ──
@Client.on_callback_query(filters.regex("^close_panel$"))
async def close_panel(client, query: CallbackQuery):
    try:
        await query.message.delete()
    except Exception:
        await query.answer("❌ Can't close panel", show_alert=True)
