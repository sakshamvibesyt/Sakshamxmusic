
import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Telegram API credentials
API_ID = int(getenv("API_ID", ""))
API_HASH = getenv("API_HASH", "")

# Telegram bot token
BOT_TOKEN = getenv("BOT_TOKEN", "")

# MongoDB
MONGO_DB_URI = getenv("MONGO_DB_URI", "")

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", "60"))

LOGGER_ID = int(getenv("LOGGER_ID", "0"))
OWNER_ID = int(getenv("OWNER_ID", "7574330905"))

# Heroku settings
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME", "")
HEROKU_API_KEY = getenv("HEROKU_API_KEY", "")

# Upstream repository
UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/NoxxOP/ShrutixMusic",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("GIT_TOKEN")

# Support links
SUPPORT_CHANNEL = getenv(
    "SUPPORT_CHANNEL",
    "https://t.me/Sakshamvenus",
)
SUPPORT_CHAT = getenv(
    "SUPPORT_CHAT",
    "https://t.me/Sakshamvenus",
)

AUTO_LEAVING_ASSISTANT = (
    getenv("AUTO_LEAVING_ASSISTANT", "False").lower() == "true"
)

# Spotify credentials
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET")

PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "25"))
TG_AUDIO_FILESIZE_LIMIT = int(
    getenv("TG_AUDIO_FILESIZE_LIMIT", "104857600")
)
TG_VIDEO_FILESIZE_LIMIT = int(
    getenv("TG_VIDEO_FILESIZE_LIMIT", "1073741824")
)

# User sessions
STRING1 = getenv("STRING_SESSION")
STRING2 = getenv("STRING_SESSION2")
STRING3 = getenv("STRING_SESSION3")
STRING4 = getenv("STRING_SESSION4")
STRING5 = getenv("STRING_SESSION5")

BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

# Shruti welcome photo:
# If blank, the bot uses START_IMG_URL.
SEMX_WELCOME_IMG_URL = getenv(
    "SEMX_WELCOME_IMG_URL", ""
).strip()

# Shruti welcome sticker file ID:
# If blank, start.py tries its built-in fallback sticker.
SEMX_WELCOME_STICKER_ID = getenv(
    "SEMX_WELCOME_STICKER_ID", ""
).strip()

START_IMG_URL = getenv(
    "START_IMG_URL",
    "https://i.ibb.co/KRdfV59/4027f92d-d204-4942-af78-0fb6319cca61.jpg",
)

PING_IMG_URL = getenv(
    "PING_IMG_URL",
    "https://i.ibb.co/KRdfV59/4027f92d-d204-4942-af78-0fb6319cca61.jpg",
)

PLAYLIST_IMG_URL = "https://te.legra.ph/file/4ec5ae4381dffb039b4ef.jpg"
STATS_IMG_URL = "https://te.legra.ph/file/e906c2def5afe8a9b9120.jpg"
TELEGRAM_AUDIO_URL = "https://te.legra.ph/file/6298d377ad3eb46711644.jpg"
TELEGRAM_VIDEO_URL = "https://te.legra.ph/file/6298d377ad3eb46711644.jpg"
STREAM_IMG_URL = "https://te.legra.ph/file/bd995b032b6bd263e2cc9.jpg"
SOUNCLOUD_IMG_URL = "https://te.legra.ph/file/bb0ff85f2dd44070ea519.jpg"
YOUTUBE_IMG_URL = "https://te.legra.ph/file/6298d377ad3eb46711644.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://te.legra.ph/file/37d163a2f75e0d3b403d6.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://te.legra.ph/file/b35fd1dfca73b950b1b05.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://te.legra.ph/file/95b3ca7993bbfaf993dcb.jpg"


def time_to_seconds(time):
    stringt = str(time)
    return sum(
        int(x) * 60 ** i
        for i, x in enumerate(reversed(stringt.split(":")))
    )


DURATION_LIMIT = int(
    time_to_seconds(f"{DURATION_LIMIT_MIN}:00")
)


if SUPPORT_CHANNEL:
    if not re.match(r"(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] SUPPORT_CHANNEL url must start with https://"
        )

if SUPPORT_CHAT:
    if not re.match(r"(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit(
            "[ERROR] SUPPORT_CHAT url must start with https://"
        )
        
