# ╔════════════════════════════════════════════════════════╗
# ║                Telegram Link Sharing Bot               ║
# ║  Secure Channel Link Sharing | Developed by @RexySama    ║
# ║                                                        ║
# ║  ⚠️ Please do not remove credits, respect developers.   ║
# ╚════════════════════════════════════════════════════════╝

import os
from os import environ
import logging
from logging.handlers import RotatingFileHandler
import re

# ╔════════════════════════════════╗
# ║       Telegram API Credentials  ║
# ╚════════════════════════════════╝
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "7716452978:AAF8zMYazok32rDAcJvtesVwQlzWnOsfEjc")
APP_ID = int(os.environ.get("APP_ID", "28744454"))
API_HASH = os.environ.get("API_HASH", "debd37cef0ad1a1ce45d0be8e8c3c5e7")

# ╔════════════════════════════════╗
# ║       Owner & Bot Information   ║
# ╚════════════════════════════════╝
OWNER_ID = int(os.environ.get("OWNER_ID", "6497757690"))
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
START_PIC_FILE_ID = "https://telegra.ph/file/f3d3aff9ec422158feb05-d2180e3665e0ac4d32.jpg"
START_IMG = START_PIC_FILE_ID
START_MSG = os.environ.get(
    "START_MESSAGE",
    "<b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ᴀᴅᴠᴀɴᴄᴇᴅ ʟɪɴᴋs sʜᴀʀɪɴɢ ʙᴏᴛ.\n\n"
    "ᴡɪᴛʜ ᴛʜɪs ʙᴏᴛ, ʏᴏᴜ ᴄᴀɴ sʜᴀʀᴇ ʟɪɴᴋs ᴀɴᴅ ᴋᴇᴇᴘ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟs "
    "sᴀғᴇ ғʀᴏᴍ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs.\n\n"
    "<blockquote>‣ ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ : <a href='https://t.me/codeflix_bots'>ʏᴀᴛᴏ</a></blockquote></b>",
)
HELP = os.environ.get(
    "HELP_MESSAGE",
    "<b><blockquote expandable>» Creator: <a href=https://t.me/proyato>Yato</a>\n"
    "» Our Community: <a href=https://t.me/otakuflix_network>Flix Network</a>\n"
    "» Anime Channel: <a href=https://t.me/animes_cruise>Anime Cruise</a>\n"
    "» Ongoing Anime: <a href=https://t.me/Ongoing_cruise>Ongoing Cruise</a>\n"
    "» Developer: <a href=https://t.me/onlyyuji>Yuji</a></b>",
)
ABOUT = os.environ.get(
    "ABOUT_MESSAGE",
    "<b><blockquote expandable>This bot is developed by Yato (@ProYato) "
    "to securely share Telegram channel links with temporary invite links, "
    "protecting your channels from copyright issues.</b>",
)

# ╔════════════════════════════════╗
# ║        Extra Texts & Channels   ║
# ╚════════════════════════════════╝
ABOUT_TXT = """<b>›› ᴄᴏᴍᴍᴜɴɪᴛʏ: <a href='https://t.me/otakuflix_network'>ᴏᴛᴀᴋᴜғʟɪx</a>
<blockquote expandable>›› ᴜᴘᴅᴀᴛᴇs: <a href='https://t.me/codeflix_bots'>Cʟɪᴄᴋ ʜᴇʀᴇ</a>
›› ᴏᴡɴᴇʀ: <a href='https://t.me/cosmic_freak'>ʏᴀᴛᴏ</a>
›› ʟᴀɴɢᴜᴀɢᴇ: <a href='https://docs.python.org/3/'>Pʏᴛʜᴏɴ 3</a>
›› ʟɪʙʀᴀʀʏ: <a href='https://docs.pyrogram.org/'>Pʏʀᴏɢʀᴀᴍ v2</a>
›› ᴅᴀᴛᴀʙᴀsᴇ: <a href='https://www.mongodb.com/docs/'>Mᴏɴɢᴏ ᴅʙ</a>
›› ᴅᴇᴠᴇʟᴏᴘᴇʀ: @ProYato</b></blockquote>"""

CHANNELS_TXT = """<b>›› ᴀɴɪᴍᴇ: <a href='https://t.me/animes_cruise'>ᴀɴɪᴍᴇ ᴄʀᴜɪsᴇ</a>
<blockquote expandable>›› ᴍᴏᴠɪᴇs: <a href='https://t.me/movieflixspot'>ᴍᴏᴠɪᴇғʟɪx</a>
›› ᴡᴇʙsᴇʀɪᴇs: <a href='https://t.me/webseries_flix'>ᴡᴇʙsᴇʀɪᴇs ғʟɪx</a>
›› ᴀᴅᴜʟᴛ: <a href='https://t.me/hanime_arena'>ᴄᴏʀɴʜᴜʙ</a>
›› ᴍᴀɴʜᴡᴀ: <a href='https://t.me/pornhwa_flix'>ᴘᴏʀɴʜᴡᴀ</a>
›› ᴄᴏᴍᴍᴜɴɪᴛʏ: <a href='https://t.me/otakuflix_network'>ᴏᴛᴀᴋᴜғʟɪx</a>
›› ᴅᴇᴠᴇʟᴏᴘᴇʀ: @ProYato</b></blockquote>"""

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
