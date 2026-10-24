
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardButton

import config
from ShrutixMusic import nand


def start_panel(_):
    return [
        [
            InlineKeyboardButton(
                text="🎧  ᴀᴅᴅ ᴛᴏ ɢʀᴏᴜᴘ",
                url=f"https://t.me/{nand.username}?startgroup=true",
                style=ButtonStyle.PRIMARY,
            )
        ],
        [
            InlineKeyboardButton(
                text="💬  sᴜᴘᴘᴏʀᴛ",
                url=config.SUPPORT_CHAT,
                style=ButtonStyle.SUCCESS,
            )
        ],
    ]


def private_panel(_):
    return [
        [
            InlineKeyboardButton(
                text="🎧  ᴀᴅᴅ ᴛᴏ ɢʀᴏᴜᴘ",
                url=f"https://t.me/{nand.username}?startgroup=true",
                style=ButtonStyle.PRIMARY,
            )
        ],
        [
            InlineKeyboardButton(
                text="⚙️  ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs",
                callback_data="settings_back_helper",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text="📢  ᴜᴘᴅᴀᴛᴇs",
                url=config.SUPPORT_CHANNEL,
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text="💬  sᴜᴘᴘᴏʀᴛ",
                url=config.SUPPORT_CHAT,
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text="👑  ᴏᴡɴᴇʀ",
                url="https://t.me/Sakshamvenus",
                style=ButtonStyle.PRIMARY,
            ),
        ],
    ]
    
