
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
    """Use custom Shruti image if configured."""
    return (
        getattr(config, "SEMX_WELCOME_IMG_URL", "").strip()
        or config.START_IMG_URL
    )


def welcome_caption(user, bot):
    """Premium Sem X Shruti welcome screen."""
    return (
        f"<b>╭━━━〔 🎧 SEM X SHRUTI 〕━━━╮</b>\n"
        f"<i>YOUR MUSIC. YOUR MOOD. YOUR WORLD.</i>\n"
        f"<b>╰━━━━━━━━━━━━━━━━━━━━━━╯</b>\n\n"

        f"Hey {user.mention}, welcome aboard! 💜\n"
        f"You are now connected to <b>{bot.mention}</b> — "
        f"your personal voice-chat music companion.\n\n"

        f"<b>┏━━━ ✦ THE EXPERIENCE ✦ ━━━┓</b>\n"
        f"🎵  <b>Instant Music</b>\n"
        f"<blockquote>Find your favourite tracks and play your vibe.</blockquote>\n"
        f"🔊  <b>Voice Chat Streaming</b>\n"
        f"<blockquote>Bring music into your group's voice chat.</blockquote>\n"
        f"🎚️  <b>Smart Playback</b>\n"
        f"<blockquote>Control your music and manage the queue.</blockquote>\n"
        f"⚡  <b>Made for the Vibe</b>\n"
        f"<blockquote>Simple commands. Smooth experience.</blockquote>\n"
        f"<b>┗━━━━━━━━━━━━━━━━━━━━━━┛</b>\n\n"

        f"💿 <b>YOUR NEXT TRACK STARTS HERE</b>\n"
        f"<code>/play song name</code>\n\n"

        f"👑 <b>CREATED BY</b>\n"
        f"<a href='https://t.me/Sakshamvenus'>Saksham Venus</a>\n\n"

        f"<i>Good music. Good people. Unmatched vibes. ✨</i>\n"
        f"👇 <b>Choose your destination below.</b>"
    )


async def play_welcome_animation(message):
    """React to /start and display a short animated intro."""
    try:
        await message.react(emoji="🎧", big=True)
    except Exception as exc:
        print(f"Welcome reaction unavailable: {exc}")

    frames = [
        (
            "<b>╭━━━〔 SEM X SHRUTI 〕━━━╮</b>\n"
            "   ◉ Establishing connection...\n"
            "   ▰▱▱▱▱▱  <i>CONNECTING</i>\n"
            "<b>╰━━━━━━━━━━━━━━━━━━━━╯</b>"
        ),
        (
            "<b>╭━━━〔 SEM X SHRUTI 〕━━━╮</b>\n"
            "   ◉ Tuning into your vibe 💜\n"
            "   ▰▰▰▰▱▱  <i>LOADING MUSIC</i>\n"
            "<b>╰━━━━━━━━━━━━━━━━━━━━╯</b>"
        ),
        (
            "<b>╭━━━〔 SEM X SHRUTI 〕━━━╮</b>\n"
            "   ◉ Your music world is ready ✨\n"
            "   ▰▰▰▰▰▰  <i>ALL SYSTEMS READY</i>\n"
            "<b>╰━━━━━━━━━━━━━━━━━━━━╯</b>"
        ),
    ]

    loader = None
    try:
        loader = await message.reply_text(
            frames[0],
            disable_web_page_preview=True,
        )

        for frame in frames[1:]:
            await asyncio.sleep(0.65)
            await loader.edit_text(
                frame,
                disable_web_page_preview=True,
            )

        await asyncio.sleep(0.35)

    except Exception as exc:
        print(f"Welcome animation error: {exc}")

    finally:
        if loader:
            try:
                await loader.delete()
            except Exception:
                pass


@nand.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    effect_id = random.choice(MESSAGE_EFFECTS)
    parts = (message.text or "").split(None, 1)
    name = parts[1] if len(parts) > 1 else ""

    if name.startswith("help"):
        keyboard = help_pannel(_)
        return await message.reply_photo(
            photo=welcome_photo(),
            caption=_[ "help_1" ].format(config.SUPPORT_CHAT),
            reply_markup=keyboard,
            effect_id=effect_id,
        )

    if name.startswith("sud"):
        await sudoers_list(client=client, message=message, _=_)
        if await is_on_off(2):
            return await nand.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"{message.from_user.mention} started the bot "
                    f"to check the <b>sudolist</b>.\n\n"
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
                await m.edit_text("❌ Couldn't find track information.")
                return

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

            key = InlineKeyboardMarkup(
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
                reply_markup=key,
            )

            if await is_on_off(2):
                await nand.send_message(
                    chat_id=config.LOGGER_ID,
                    text=(
                        f"{message.from_user.mention} checked track information.\n\n"
                        f"<b>User ID:</b> <code>{message.from_user.id}</code>\n"
                        f"<b>Username:</b> @{message.from_user.username}"
                    ),
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


@nand.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)

    await message.reply_photo(
        photo=welcome_photo(),
        caption=_[ "start_1" ].format(nand.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
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

                out = start_panel(_)
                await message.reply_photo(
                    photo=welcome_photo(),
                    caption=_[ "start_3" ].format(
                        message.from_user.first_name,
                        nand.mention,
                        message.chat.title,
                        nand.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()

        except Exception as exc:
            print(f"Group welcome error: {exc}")
    
