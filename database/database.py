# +++ Modified By Yato [telegram username: @i_killed_my_clan & @ProYato] +++ #
import motor.motor_asyncio
import base64
from config import DB_URI, DB_NAME
from datetime import datetime, timedelta
from typing import List, Optional

# ----------------- DATABASE CLIENT ----------------- #
dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]

# ----------------- COLLECTIONS ----------------- #
user_data = database['users']
channels_collection = database['channels']
fsub_channels_collection = database['fsub_channels']
admins_collection = database['admins']

# ----------------- USER MANAGEMENT ----------------- #
async def add_user(user_id: int) -> bool:
    if not isinstance(user_id, int) or user_id <= 0:
        return False
    try:
        if await user_data.find_one({'_id': user_id}):
            return False
        await user_data.insert_one({'_id': user_id, 'created_at': datetime.utcnow()})
        return True
    except Exception as e:
        print(f"Error adding user {user_id}: {e}")
        return False

async def present_user(user_id: int) -> bool:
    if not isinstance(user_id, int):
        return False
    return bool(await user_data.find_one({'_id': user_id}))

async def full_userbase() -> List[int]:
    try:
        user_docs = user_data.find()
        return [doc['_id'] async for doc in user_docs]
    except Exception as e:
        print(f"Error fetching userbase: {e}")
        return []

async def del_user(user_id: int) -> bool:
    try:
        result = await user_data.delete_one({'_id': user_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting user {user_id}: {e}")
        return False

# ----------------- ADMIN MANAGEMENT ----------------- #
async def is_admin(user_id: int) -> bool:
    try:
        user_id = int(user_id)
        return bool(await admins_collection.find_one({'_id': user_id}))
    except Exception as e:
        print(f"Error checking admin {user_id}: {e}")
        return False

async def add_admin(user_id: int) -> bool:
    try:
        user_id = int(user_id)
        await admins_collection.update_one({'_id': user_id}, {'$set': {'_id': user_id}}, upsert=True)
        return True
    except Exception as e:
        print(f"Error adding admin {user_id}: {e}")
        return False

async def remove_admin(user_id: int) -> bool:
    try:
        result = await admins_collection.delete_one({'_id': user_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error removing admin {user_id}: {e}")
        return False

async def list_admins() -> List[int]:
    try:
        admins = await admins_collection.find().to_list(None)
        return [admin['_id'] for admin in admins]
    except Exception as e:
        print(f"Error listing admins: {e}")
        return []

# ----------------- CHANNEL MANAGEMENT ----------------- #
async def save_channel(channel_id: int) -> bool:
    if not isinstance(channel_id, int):
        return False
    try:
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {"$set": {"channel_id": channel_id, "invite_link_expiry": None, "created_at": datetime.utcnow(), "status": "active"}},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error saving channel {channel_id}: {e}")
        return False

async def get_channels() -> List[int]:
    try:
        channels = await channels_collection.find({"status": "active"}).to_list(None)
        return [c['channel_id'] for c in channels if 'channel_id' in c]
    except Exception as e:
        print(f"Error fetching channels: {e}")
        return []

async def delete_channel(channel_id: int) -> bool:
    try:
        result = await channels_collection.delete_one({"channel_id": channel_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting channel {channel_id}: {e}")
        return False

async def save_encoded_link(channel_id: int) -> Optional[str]:
    try:
        encoded_link = base64.urlsafe_b64encode(str(channel_id).encode()).decode()
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {"$set": {"encoded_link": encoded_link, "status": "active", "updated_at": datetime.utcnow()}},
            upsert=True
        )
        return encoded_link
    except Exception as e:
        print(f"Error saving encoded link {channel_id}: {e}")
        return None

async def get_channel_by_encoded_link(encoded_link: str) -> Optional[int]:
    try:
        channel = await channels_collection.find_one({"encoded_link": encoded_link, "status": "active"})
        return channel["channel_id"] if channel and "channel_id" in channel else None
    except Exception as e:
        print(f"Error fetching channel by encoded link {encoded_link}: {e}")
        return None

async def save_invite_link(channel_id: int, invite_link: str, is_request: bool) -> bool:
    try:
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {"$set": {"current_invite_link": invite_link, "is_request_link": is_request, "invite_link_created_at": datetime.utcnow(), "status": "active"}},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error saving invite link {channel_id}: {e}")
        return False

async def get_current_invite_link(channel_id: int) -> Optional[dict]:
    try:
        channel = await channels_collection.find_one({"channel_id": channel_id, "status": "active"})
        if channel and "current_invite_link" in channel:
            return {"invite_link": channel["current_invite_link"], "is_request": channel.get("is_request_link", False)}
        return None
    except Exception as e:
        print(f"Error fetching current invite link {channel_id}: {e}")
        return None

# ----------------- FORCE-SUB CHANNELS ----------------- #
async def add_fsub_channel(channel_id: int) -> bool:
    if not isinstance(channel_id, int):
        return False
    try:
        if await fsub_channels_collection.find_one({'channel_id': channel_id}):
            return False
        await fsub_channels_collection.insert_one({'channel_id': channel_id, 'created_at': datetime.utcnow(), 'mode': 'off', 'status': 'active'})
        return True
    except Exception as e:
        print(f"Error adding FSub channel {channel_id}: {e}")
        return False

async def remove_fsub_channel(channel_id: int) -> bool:
    try:
        result = await fsub_channels_collection.delete_one({'channel_id': channel_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error removing FSub channel {channel_id}: {e}")
        return False

async def get_fsub_channels() -> List[int]:
    try:
        channels = await fsub_channels_collection.find({'status': 'active'}).to_list(None)
        return [c['channel_id'] for c in channels if 'channel_id' in c]
    except Exception as e:
        print(f"Error fetching FSub channels: {e}")
        return []

async def channel_exist(channel_id: int) -> bool:
    try:
        found = await fsub_channels_collection.find_one({'channel_id': channel_id})
        return bool(found)
    except Exception as e:
        print(f"Error checking FSub channel existence {channel_id}: {e}")
        return False

async def get_channel_mode(channel_id: int) -> str:
    try:
        doc = await fsub_channels_collection.find_one({'channel_id': channel_id})
        return doc.get('mode', 'off') if doc else 'off'
    except Exception as e:
        print(f"Error fetching FSub channel mode {channel_id}: {e}")
        return 'off'

async def set_channel_mode(channel_id: int, mode: str):
    try:
        await fsub_channels_collection.update_one({'channel_id': channel_id}, {'$set': {'mode': mode}}, upsert=True)
    except Exception as e:
        print(f"Error setting FSub channel mode {channel_id}: {e}")

# ----------------- APPROVAL MANAGEMENT ----------------- #
async def set_approval_off(channel_id: int, off: bool = True) -> bool:
    """Set approval_off flag for a channel."""
    if not isinstance(channel_id, int):
        return False
    try:
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {"$set": {"approval_off": off}},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error setting approval_off for channel {channel_id}: {e}")
        return False

async def is_approval_off(channel_id: int) -> bool:
    """Check if approval_off flag is set for a channel."""
    if not isinstance(channel_id, int):
        return False
    try:
        channel = await channels_collection.find_one({"channel_id": channel_id})
        return bool(channel and channel.get("approval_off", False))
    except Exception as e:
        print(f"Error checking approval_off for channel {channel_id}: {e}")
        return False
