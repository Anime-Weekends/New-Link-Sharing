# ╭───────────────────────────────────────────────╮
# │                  Bot Startup                  │
# ╰───────────────────────────────────────────────╯

import asyncio
import sys
from datetime import datetime

from pyrogram import Client
from pyrogram.enums import ParseMode
import pyrogram.utils
from aiohttp import web

from config import (
    API_HASH,
    APP_ID,
    LOGGER,
    TG_BOT_TOKEN,
    TG_BOT_WORKERS,
    PORT,
    OWNER_ID,
)
from plugins import web_server


# ╭───────────────────────────────────────────────╮
# │ Pyrogram Config                               │
# ╰───────────────────────────────────────────────╯

pyrogram.utils.MIN_CHANNEL_ID = -1009147483647

# Bot startup message
STARTUP_MESSAGE = "Links Sharing Started"


# ╭───────────────────────────────────────────────╮
# │ Bot Class Definition                          │
# ╰───────────────────────────────────────────────╯

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN,
        )
        self.LOGGER = LOGGER

    async def start(self, *args, **kwargs):
        await super().start()
        self.uptime = datetime.now()

        # Bot info
        usr_bot_me = await self.get_me()
        self.username = usr_bot_me.username
        self.set_parse_mode(ParseMode.HTML)

        # Notify owner of bot restart
        try:
            await self.send_message(
                chat_id=OWNER_ID,
                text="<b><blockquote>🤖 Bot Restarted ♻️</blockquote></b>",
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            self.LOGGER(__name__).warning(
                f"Failed to notify owner ({OWNER_ID}) of bot start: {e}"
            )

        self.LOGGER(__name__).info("Bot Running..!\n\nCreated by https://t.me/ProObito")
        self.LOGGER(__name__).info(f"{STARTUP_MESSAGE}")

        # Start web server
        try:
            app_runner = web.AppRunner(await web_server())
            await app_runner.setup()
            bind_address = "0.0.0.0"
            await web.TCPSite(app_runner, bind_address, PORT).start()
            self.LOGGER(__name__).info(f"Web server started on {bind_address}:{PORT}")
        except Exception as e:
            self.LOGGER(__name__).error(f"Failed to start web server: {e}")

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")


# ╭───────────────────────────────────────────────╮
# │ Global Broadcast Cancel Flag                  │
# ╰───────────────────────────────────────────────╯

is_canceled = False
cancel_lock = asyncio.Lock()


# ╭───────────────────────────────────────────────╮
# │ Main Entry Point                              │
# ╰───────────────────────────────────────────────╯

if __name__ == "__main__":
    Bot().run()

# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
#     ✧ R ᴇ x ʏ   -   レクシィ   -   Dᴇᴠ ✧
# ✦━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦
