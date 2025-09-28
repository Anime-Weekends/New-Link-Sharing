# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
#     ✧ R ᴇ x ʏ   -   レクシィ   -   Dᴇᴠ ✧
# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦

import os
from os import environ
import logging
from logging.handlers import RotatingFileHandler
import re

# ╔════════════════════════════════╗
# ║       Telegram API Credentials  ║
# ╚════════════════════════════════╝

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "8356974733:AAETAobZZyp77cU8CGhhEXkfRC3rfCZOaAY")
APP_ID = int(os.environ.get("APP_ID", "28744454"))
API_HASH = os.environ.get("API_HASH", "debd37cef0ad1a1ce45d0be8e8c3c5e7")

# ╔════════════════════════════════╗
# ║       Owner & Bot Information   ║
# ╚════════════════════════════════╝

OWNER_ID = int(os.environ.get("OWNER_ID", "6266529037"))
PORT = os.environ.get("PORT", "8080")

# ╔════════════════════════════════╗
# ║       Database Configuration    ║
# ╚════════════════════════════════╝

DB_URI = os.environ.get("DB_URI", "mongodb+srv://Rexybecomenice:Rexybecomenice@cluster0.4oosu31.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DB_NAME", "link")

# ╔════════════════════════════════╗
# ║        Auto Approve Settings    ║
# ╚════════════════════════════════╝

id_pattern = re.compile(r"^-?\d+$")  # Regex for chat IDs
CHAT_ID = [
    int(app_chat_id) if id_pattern.search(app_chat_id) else app_chat_id
    for app_chat_id in environ.get("CHAT_ID", "").split()
]
TEXT = environ.get(
    "APPROVED_WELCOME_TEXT",
    "<b>{mention},\n\nʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ {title} ɪs ᴀᴘᴘʀᴏᴠᴇᴅ.\n‣ ᴘᴏᴡᴇʀᴇᴅ ʙʏ @Codeflix_Bots</b>",
)
APPROVED = environ.get("APPROVED_WELCOME", "on").lower()

# ╔════════════════════════════════╗
# ║        Default Configurations   ║
# ╚════════════════════════════════╝

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "40"))

# ╔════════════════════════════════╗
# ║        Start & Help Messages    ║
# ╚════════════════════════════════╝

START_PIC_FILE_ID = "https://i.ibb.co/kNm80v1/photo-2025-08-12-19-47-36-7537788116967358496.jpg"
START_IMG = "https://telegra.ph/HgBotz-09-25"
START_MSG = os.environ.get(
    "START_MESSAGE",
    "ㅤ\n"
    "<blockquote>≡ 𝗜'𝗠 𝗟𝗜𝗡𝗞 𝗦𝗛𝗔𝗥𝗜𝗡𝗚 𝗕𝗢𝗧, ʟɪɴᴋ ᴍᴀɴᴀɢᴇʀ ʙᴏᴛ ᴅᴇsɪɢɴᴇᴅ ᴇxᴄʟᴜsɪᴠᴇʟʏ ғᴏʀ <b>ᴇᴍɪɴᴇɴᴄᴇ sᴏᴄɪᴇᴛʏ.</b></blockquote>\n\n"
    "<blockquote>≡ 𝗙𝗨𝗟𝗟𝗬 𝗔𝗗𝗩𝗔𝗡𝗖𝗘𝗗 ʟɪɴᴋ sʜᴀʀɪɴɢ sʏsᴛᴇᴍ ᴡɪᴛʜ ᴄᴏᴏʟᴅᴏᴡɴ, ɪɴᴠɪᴛᴇ ᴛʀᴀᴄᴋɪɴɢ & ᴍᴏʀᴇ.</blockquote>\n"
    "ㅤ",
)

# ╔════════════════════════════════╗
# ║        Extra Texts & Channels   ║
# ╚════════════════════════════════╝

ABOUT_TXT = """ㅤ\n<b><blockquote>◈ Mʏ ɴᴀᴍᴇ : <a href='https://t.me/AnimeWeekendBot'>ᴀᴅᴠ ʟɪɴᴋ sʜᴀʀɪɴɢ</blockquote></a>
<blockquote expandable>◈ Oᴡɴᴇʀ : <a href='tg://openmessage?user_id=6266529037'>R ᴇ x ʏ - レクシィ</a>
◈ Dᴇᴠᴇʟᴏᴘᴇʀ : <a href='https://t.me/RexySama'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>
◈ ʟᴀɴɢᴜᴀɢᴇ : <a href='https://docs.python.org/3/'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>
◈ ʟɪʙʀᴀʀʏ : <a href='https://docs.pyrogram.org/'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>
◈ ᴅᴀᴛᴀʙᴀsᴇ : <a href='https://www.mongodb.com/docs/'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a></blockquote></b>\nㅤ"""

CHANNELS_TXT = """ㅤ\n<blockquote expandable><b>◈ Aɴɪᴍᴇ Cʜᴀɴɴᴇʟ : <a href='https://t.me/Anime_Weekends'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>
◈ Oɴɢᴏɪɴɢ Cʜᴀɴɴᴇʟ : <a href=''>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>
◈ Aɴɪᴍᴇ Iɴᴅᴇx Cʜᴀɴɴᴇʟ :  <a href='https://t.me/+zc1zoff06ZVjNWU1'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>
◈ Kᴅʀᴀᴍᴀ Cʜᴀɴɴᴇʟ : <a href='https://t.me/Kdrama_Weekends'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>
◈ Wᴇʙsᴇʀɪᴇs Cʜᴀɴɴᴇʟ : <a href='https://t.me/+A7l9mm0Q1VJjODc9'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>
◈ Mᴀɴɢᴀ Cʜᴀɴɴᴇʟ : <a href='https://t.me/Manga_Weekend'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>
◈ Cᴜʟᴛᴜʀᴇᴅ Cʜᴀɴɴᴇʟ : <a href='https://t.me/Cultured_Weekends'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a></b></blockquote>\nㅤ"""

# ╔════════════════════════════════╗
# ║             Bot Texts           ║
# ╚════════════════════════════════╝

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "⚠️ ғᴜᴄᴋ ʏᴏᴜ, ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴍʏ ᴍᴀsᴛᴇʀ. ɢᴏ ᴀᴡᴀʏ, ʙɪᴛᴄʜ 🙃!"

# ╔════════════════════════════════╗
# ║          Logging Setup          ║
# ╚════════════════════════════════╝

LOG_FILE_NAME = "links-sharingbot.txt"
DATABASE_CHANNEL = int(os.environ.get("DATABASE_CHANNEL", "-1002624286889"))  # Channel where user links are stored

try:
    ADMINS = []
    for x in (os.environ.get("ADMINS", "6266529037").split()):
        ADMINS.append(int(x))
except ValueError:
    raise Exception("Your Admins list does not contain valid integers.")

# Ensure OWNER is always admin
ADMINS.append(OWNER_ID)
ADMINS.append(6266529037)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# ╔════════════════════════════════╗
# ║          Logger Function        ║
# ╚════════════════════════════════╝

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)

# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
#     ✧ R ᴇ x ʏ   -   レクシィ   -   Dᴇᴠ ✧
# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
