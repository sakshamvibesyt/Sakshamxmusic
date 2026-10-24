
import asyncio
import random
import time

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from py_yt import VideosSearch

import config
from ShrutixMusic import nand
from ShrutixMusic.misc import _boot_
from ShrutixMusic.plugins.sudo.sudoers import sudoers_list
from ShrutixMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from ShrutixMusic.utils.decorators.language import LanguageStart
from ShrutixMusic.utils.formatters import get_readable_time
from ShrutixMusic.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string


MESSAGE_EFFECTS = [
    5107584321108051014,
    5159385139981059251,
    5104841245755180586,
    5046509860389126442,
]


def welcome_photo():
    return (
        getattr(config, "SEMX_WELCOME_IMG_URL", "").strip()
        or config.START_IMG_URL
    )


def welcome_caption(user, bot):
    """Compact welcome with expandable premium details."""
    return (
        f"🎧 <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ</b>\n"
        f"<b>sᴇᴍ x sʜʀᴜᴛɪ ʙᴏᴛ 💜</b>\n\n"
        f"✦ ʜᴇʏ, {user.mention} ✨\n"
        f"<i>ʏᴏᴜʀ ᴍᴜsɪᴄ. ʏᴏᴜʀ ᴠɪʙᴇ.</i>\n\n"
        f"<blockquote expandable>"
        f"💜 <b>ʏᴏᴜʀ ᴘᴇʀsᴏɴᴀʟ ᴍᴜsɪᴄ ᴜɴɪᴠᴇʀsᴇ!</b>\n\n"
        f"🎵 <b>ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs</b>\n"
        f"┊ 🎶 ᴍᴜsɪᴄ sᴛʀᴇᴀᴍɪɴɢ\n"
        f"┊ 🎙️ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴍᴜsɪᴄ\n"
        f"┊ 🤖 sᴍᴀʀᴛ ᴀssɪsᴛᴀɴᴛ\n\n"
        f"🎧 <b>ᴛʀʏ ɪᴛ ɴᴏᴡ</b>\n"
        f"<code>/play song name</code>\n\n"
        f"👑 <b>ᴏᴡɴᴇʀ:</b> "
        f"<a href='https://t.me/Sakshamvenus'>Saksham Venus</a>\n"
        f"⚡ <b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ sᴇᴍ x sʜʀᴜᴛɪ</b>\n\n"
        f"💜 ᴍᴜsɪᴄ ɪs ᴍᴏʀᴇ ᴛʜᴀɴ sᴏᴜɴᴅ — ɪᴛ's ᴀ ᴠɪʙᴇ!\n"
        f"</blockquote>\n\n"
        f"🫧 <i>ᴛᴀᴘ ᴛᴏ ʀᴇᴠᴇᴀʟ ᴛʜᴇ ᴍᴀɢɪᴄ</i> 💜\n"
        f"👇 <b>ᴄʜᴏᴏsᴇ ʏᴏᴜʀ ᴏᴘᴛɪᴏɴ</b>"
    )


async def send_welcome_sticker(message):
    """Send the configured welcome sticker, if one is set."""
    sticker_id = getattr(
        config, "SEMX_WELCOME_STICKER_ID", ""
    ).strip()

    if not sticker_id:
        return

    try:
        await message.reply_sticker(sticker=sticker_id)
    except Exception as exc:
        print(f"Welcome sticker unavailable: {exc}")


async def play_welcome_animation(message):
    """Short loading animation and reaction."""
    try:
        await message.react(emoji="🎧", big=True)
    except Exception as exc:
        print(f"Welcome reaction unavailable: {exc}")

    frames = [
        (
            "💜 <b>SEM X SHRUTI</b>\n"
            "◉ Connecting to your vibe...\n"
            "▰▱▱▱▱▱ <i>LOADING</i>"
        ),
        (
            "🎧 <b>SEM X SHRUTI</b>\n"
            "◉ Tuning into your music...\n"
            "▰▰▰▰▱▱ <i>ALMOST READY</i>"
        ),
        (
            "✨ <b>YOUR MUSIC IS READY</b>\n"
            "◉ Let the vibe begin!\n"
            "▰▰▰▰▰▰ <i>CONNECTED</i>"
        ),
    ]

    loader = None
    try:
        loader = await message.reply_text(
            frames[0],
            disable_web_page_preview=True,
        )

        for frame in frames[1:]:
            await asyncio.sleep(0.7)
            await loader.edit_text(
                frame,
                disable_web_page_preview=True,
            )

        await asyncio.sleep(0.3)

    except Exception as exc:
        print(f"Welcome animation error: {exc}")

    finally:
        if loader:
            try:
                await loader.delete()
            except Exception:
                pass


@nand.on_message(
    filters.command(["start"]) & filters.private & ~BANNED_USERS
)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    effect_id = random.choice(MESSAGE_EFFECTS)
    parts = (message.text or "").split(None, 1)
    name = parts[1] if len(parts) > 1 else ""

    if name.startswith("help"):
        return await message.reply_photo(
            photo=welcome_photo(),
            caption=_[ "help_1" ].format(config.SUPPORT_CHAT),
            reply_markup=help_pannel(_),
            effect_id=effect_id,
        )

    if name.startswith("sud"):
        await sudoers_list(client=client, message=message, _=_)
        if await is_on_off(2):
            return await nand.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"{message.from_user.mention} checked the sudolist.\n\n"
                    f"<b>User ID:</b> <code>{message.from_user.id}</code>\n"
                    f"<b>Username:</b> @{message.from_user.username}"
                ),
            )
        return

    if name.startswith("inf"):
        m = await message.reply_text("🔎 Finding track information...")
        try:
            query = str(name).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            result_list = (await results.next())["result"]

            if not result_list:
                return await m.edit_text(
                    "❌ Couldn't find track information."
                )

            result = result_list[0]
            title = result["title"]
            duration = result["duration"]
            views = result["viewCount"]["short"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            channellink = result["channel"]["link"]
            channel = result["channel"]["name"]
            link = result["link"]
            published = result["publishedTime"]

            searched_text = _["start_6"].format(
                title,
                duration,
                views,
                published,
                channellink,
                channel,
                nand.mention,
            )

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=_[ "S_B_8" ],
                            url=link,
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=_[ "S_B_9" ],
                            url=config.SUPPORT_CHAT,
                        )
                    ],
                ]
            )

            await m.delete()
            await nand.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=keyboard,
            )

        except Exception as exc:
            print(f"Track info error: {exc}")
            try:
                await m.edit_text(
                    "⚠️ Couldn't load track information. Please try again."
                )
            except Exception:
                pass
        return

    await play_welcome_animation(message)
    await send_welcome_sticker(message)

    await message.reply_photo(
        photo=welcome_photo(),
        caption=welcome_caption(message.from_user, nand),
        reply_markup=InlineKeyboardMarkup(private_panel(_)),
        effect_id=effect_id,
    )

    if await is_on_off(2):
        return await nand.send_message(
            chat_id=config.LOGGER_ID,
            text=(
                f"{message.from_user.mention} started the bot.\n\n"
                f"<b>User ID:</b> <code>{message.from_user.id}</code>\n"
                f"<b>Username:</b> @{message.from_user.username}"
            ),
        )


@nand.on_message(
    filters.command(["start"]) & filters.group & ~BANNED_USERS
)
@LanguageStart
async def start_gp(client, message: Message, _):
    uptime = int(time.time() - _boot_)

    await message.reply_photo(
        photo=welcome_photo(),
        caption=_[ "start_1" ].format(
            nand.mention, get_readable_time(uptime)
        ),
        reply_markup=InlineKeyboardMarkup(start_panel(_)),
    )
    return await add_served_chat(message.chat.id)


@nand.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except Exception:
                    pass

            if member.id == nand.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await nand.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            nand.mention,
                            f"https://t.me/{nand.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await nand.leave_chat(message.chat.id)

                await message.reply_photo(
                    photo=welcome_photo(),
                    caption=_[ "start_3" ].format(
                        message.from_user.first_name,
                        nand.mention,
                        message.chat.title,
                        nand.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(start_panel(_)),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()

        except Exception as exc:
            print(f"Group welcome error: {exc}")
            
