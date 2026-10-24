
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardButton

import config
from ShrutixMusic import nand


def start_panel(_):
    return [
        [
            InlineKeyboardButton(
                text="➕  ADD TO GROUP",
                url=f"https://t.me/{nand.username}?startgroup=true",
                style=ButtonStyle.PRIMARY,
            )
        ],
        [
            InlineKeyboardButton(
                text="💬  SUPPORT",
                url=config.SUPPORT_CHAT,
                style=ButtonStyle.SUCCESS,
            )
        ],
    ]


def private_panel(_):
    return [
        [
            InlineKeyboardButton(
                text="🎧  ADD SHRUTI TO YOUR GROUP",
                url=f"https://t.me/{nand.username}?startgroup=true",
                style=ButtonStyle.PRIMARY,
            )
        ],
        [
            InlineKeyboardButton(
                text="⚙️  HELP & COMMANDS",
                callback_data="settings_back_helper",
                style=ButtonStyle.SUCCESS,
            )
        ],
        [
            InlineKeyboardButton(
                text="📢  UPDATES CHANNEL",
                url=config.SUPPORT_CHANNEL,
                style=ButtonStyle.PRIMARY,
            )
        ],
        [
            InlineKeyboardButton(
                text="💬  SUPPORT CHAT",
                url=config.SUPPORT_CHAT,
                style=ButtonStyle.SUCCESS,
            )
        ],
        [
            InlineKeyboardButton(
                text="👑  DEVELOPER • SAKSHAM VENUS",
                url="https://t.me/Sakshamvenus",
                style=ButtonStyle.PRIMARY,
            )
        ],
    ]
    
