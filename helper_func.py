# ╭───────────────────────────────────────────────╮
# │           Utilities & Custom Filters          │
# ╰───────────────────────────────────────────────╯

import base64
import re
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.filters import Filter

from config import OWNER_ID, ADMINS
from database.database import is_admin


# ╭───────────────────────────────────────────────╮
# │ Custom Filters                                │
# ╰───────────────────────────────────────────────╯

class IsAdmin(Filter):
    """Filter for checking if a user is an admin in DB."""
    async def __call__(self, client, message):
        return await is_admin(message.from_user.id)


is_admin_filter = IsAdmin()


class IsOwnerOrAdmin(Filter):
    """Filter for checking if a user is the bot owner or admin."""
    async def __call__(self, client, message):
        user_id = message.from_user.id
        return user_id == OWNER_ID or await is_admin(user_id)


is_owner_or_admin = IsOwnerOrAdmin()


# ╭───────────────────────────────────────────────╮
# │ Base64 Encode / Decode Utilities              │
# ╰───────────────────────────────────────────────╯

async def encode(string: str) -> str:
    """Encode a string to URL-safe Base64 without padding."""
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return base64_bytes.decode("ascii").rstrip("=")


async def decode(base64_string: str) -> str:
    """Decode a URL-safe Base64 string (handles missing padding)."""
    base64_string = base64_string.rstrip("=")
    padded = base64_string + "=" * (-len(base64_string) % 4)
    string_bytes = base64.urlsafe_b64decode(padded.encode("ascii"))
    return string_bytes.decode("ascii")


# ╭───────────────────────────────────────────────╮
# │ Readable Time Utility                          │
# ╰───────────────────────────────────────────────╯


def get_readable_time(seconds: int) -> str:
    """
    Convert seconds to a human-readable string.
    Format: days:h:m:s or h:m:s.
    """
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)

        if seconds == 0 and remainder == 0:
            break

        time_list.append(int(result))
        seconds = int(remainder)

    # Add days separately if present
    if len(time_list) == 4:
        up_time += f"{time_list.pop()},"  # pop days

    # Reverse for proper order: h:m:s
    time_list.reverse()
    up_time += ":".join(f"{val}{time_suffix_list[idx]}" for idx, val in enumerate(time_list))

    return up_time

# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
#     ✧ R ᴇ x ʏ   -   レクシィ   -   Dᴇᴠ ✧
# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
