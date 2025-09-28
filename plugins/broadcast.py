import asyncio
from datetime import datetime, timedelta
from pyrogram import Client as Bot, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from helpers import full_userbase, del_user  # adjust import

# Global variables
is_canceled = False
cancel_lock = asyncio.Lock()

user_message_count = {}
user_banned_until = {}

MAX_MESSAGES = 3
TIME_WINDOW = timedelta(seconds=10)
BAN_DURATION = timedelta(hours=1)

