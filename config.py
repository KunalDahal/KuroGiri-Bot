import asyncio
import os
import logging
from logging.handlers import RotatingFileHandler
from urllib.parse import quote_plus

username = quote_plus("filesharebot")
password = quote_plus("offline_gandu@321")

#Bot token @Botfather, --⚠️ REQUIRED--
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "7733891443:AAHccGll2QX6LYUz_g8f2neODst8zkWbHCU")

#Your API ID from my.telegram.org, --⚠️ REQUIRED--
APP_ID = int(os.environ.get("APP_ID", "37747964"))

#Your API Hash from my.telegram.org, --⚠️ REQUIRED--
API_HASH = os.environ.get("API_HASH", "b9f386527d3004080129ceaa8d2e2d3b")

#Your db channel Id --⚠️ REQUIRED--
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002217183599"))

#OWNER ID --⚠️ REQUIRED--
OWNER_ID = int(os.environ.get("OWNER_ID", "7535950439"))

#SUPPORT_GROUP: This is used for normal users for getting help if they don't understand how to use the bot --⚠ OPTIONAL--
SUPPORT_GROUP = os.environ.get("SUPPORT_GROUP", "https://t.me/Animes_Ocean_Group")

#Port
PORT = os.environ.get("PORT", "8089")

#Database --⚠️ REQUIRED--
DB_URI = f"mongodb+srv://{username}:{password}@igivefun.xmmog6e.mongodb.net/?retryWrites=true&w=majority"

DB_NAME = os.environ.get("DATABASE_NAME", "aqua2")

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))

#Collection of pics for Bot // #Optional but atleast one pic link should be replaced if you don't want predefined links
PICS = (os.environ.get("PICS", "https://i.ibb.co/7J9t8FXy/x.jpg")).split() #Required

#set your Custom Caption here, Keep None for Disable Custom Caption
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "<b><blockquote>⋆˙⟡ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ: <a href='https://t.me/Anime_Ocean_Official'>ᴀɴɪᴍᴇs ᴏᴄᴇᴀɴ</a></blockquote><b/>")

LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
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


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
