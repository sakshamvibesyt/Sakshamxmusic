import asyncio
import os
import re
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist


# ============================================================
# YouTube platform helper
# No paid API / API key / external downloader API required.
#
# Requirements:
#   pip install yt-dlp py-yt
#   ffmpeg must be available on the system.
# ============================================================

DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "downloads")

AUDIO_DOWNLOAD_PATH = os.path.abspath(
    os.path.expanduser(os.environ.get("AUDIO_DOWNLOAD_PATH", "").strip())
) if os.environ.get("AUDIO_DOWNLOAD_PATH", "").strip() else ""

VIDEO_DOWNLOAD_PATH = os.path.abspath(
    os.path.expanduser(os.environ.get("VIDEO_DOWNLOAD_PATH", "").strip())
) if os.environ.get("VIDEO_DOWNLOAD_PATH", "").strip() else ""

AUDIO_EXTENSIONS = ("webm", "m4a", "mp3", "opus", "ogg")
VIDEO_EXTENSIONS = ("mp4", "mkv", "webm")


def _clean_youtube_url(link: str) -> str:
    """Normalize a YouTube URL or video ID."""
    link = str(link).strip()

    if not link:
        return ""

    if "youtube.com/watch" in link:
        match = re.search(r"[?&]v=([A-Za-z0-9_-]{6,})", link)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(1)}"

    if "youtu.be/" in link:
        match = re.search(r"youtu\.be/([A-Za-z0-9_-]{6,})", link)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(1)}"

    if re.fullmatch(r"[A-Za-z0-9_-]{6,}", link):
        return f"https://www.youtube.com/watch?v={link}"

    return link.split("&")[0]


def _video_id(link: str) -> str:
    match = re.search(r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{6,})", str(link))
    return match.group(1) if match else ""


def _find_external(directory: str, video_id: str, extensions) -> str | None:
    if not directory or not video_id:
        return None

    for ext in extensions:
        path = os.path.join(directory, f"{video_id}.{ext}")
        if os.path.isfile(path) and os.path.getsize(path) > 0:
            return path

    return None


def time_to_seconds(time):
    stringt = str(time)
    if not stringt or stringt == "None":
        return 0

    try:
        return sum(
            int(x) * 60 ** i
            for i, x in enumerate(reversed(stringt.split(":")))
        )
    except (TypeError, ValueError):
        return 0


def _audio_ydl_options(output_path: str):
    return {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "source_address": "0.0.0.0",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }


def _video_ydl_options(output_path: str):
    return {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": output_path,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "source_address": "0.0.0.0",
    }


def _download_sync(link: str, kind: str, output_file: str) -> str | None:
    """Download media directly with yt-dlp. No external API is used."""
    url = _clean_youtube_url(link)

    if not url:
        return None

    try:
        if kind == "audio":
            opts = _audio_ydl_options(output_file)
        else:
            opts = _video_ydl_options(output_file)

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # yt-dlp may change the final extension after post-processing.
        requested = os.path.splitext(output_file)[0]
        candidates = [
            output_file,
            f"{requested}.mp3",
            f"{requested}.mp4",
            f"{requested}.m4a",
            f"{requested}.webm",
        ]

        for path in candidates:
            if os.path.isfile(path) and os.path.getsize(path) > 0:
                return path

        # Last-resort lookup in the download directory.
        directory = os.path.dirname(output_file) or "."
        prefix = os.path.basename(requested)

        if os.path.isdir(directory):
            for name in os.listdir(directory):
                if name.startswith(prefix + "."):
                    path = os.path.join(directory, name)
                    if os.path.isfile(path) and os.path.getsize(path) > 0:
                        return path

        return None

    except Exception:
        return None


async def _download_media(link: str, kind: str, timeout: int) -> str | None:
    video_id = _video_id(link)

    if not video_id:
        # Try resolving a normal YouTube URL through yt-dlp even if the ID
        # wasn't extracted by our small helper.
        video_id = re.sub(r"[^A-Za-z0-9_-]", "", str(link))[:80]

    if not video_id:
        return None

    is_audio = kind == "audio"
    external = AUDIO_DOWNLOAD_PATH if is_audio else VIDEO_DOWNLOAD_PATH
    extensions = AUDIO_EXTENSIONS if is_audio else VIDEO_EXTENSIONS

    if external:
        found = _find_external(external, video_id, extensions)
        if found:
            return found

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    base_name = os.path.join(
        DOWNLOAD_DIR,
        video_id
    )

    expected = f"{base_name}.mp3" if is_audio else f"{base_name}.mp4"

    if os.path.isfile(expected) and os.path.getsize(expected) > 0:
        return expected

    try:
        return await asyncio.wait_for(
            asyncio.to_thread(
                _download_sync,
                link,
                kind,
                expected,
            ),
            timeout=timeout,
        )
    except (asyncio.TimeoutError, Exception):
        return None


async def download_song(link: str) -> str | None:
    return await _download_media(link, "audio", 300)


async def download_video(link: str) -> str | None:
    return await _download_media(link, "video", 600)


# ============================================================
# Autoplay
# Uses YouTube search directly instead of a paid API.
# ============================================================

AUTOPLAY_REQUEST_TIMEOUT = 30
AUTOPLAY_MAX_RESULTS = 10


async def get_autoplay(
    video_id: str,
    timeout: int = AUTOPLAY_REQUEST_TIMEOUT,
    retries: int = 2,
    seed_id: str = None,
) -> list:
    """Return YouTube video IDs related to the current track.

    This replaces the old paid /autoplay API endpoint.
    """
    del retries

    seed = seed_id or video_id
    if not seed:
        return []

    seed_url = _clean_youtube_url(seed)

    try:
        def search_related():
            opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": True,
                "skip_download": True,
                "noplaylist": True,
            }

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(seed_url, download=False)

                title = info.get("title", "")
                channel = info.get("channel", "")

                query = title
                if channel:
                    query = f"{title} {channel}"

                result = ydl.extract_info(
                    f"ytsearch{AUTOPLAY_MAX_RESULTS}:{query}",
                    download=False,
                )

                tracks = []
                for entry in (result.get("entries") or []):
                    vid = entry.get("id")
                    if vid and vid != seed:
                        tracks.append(vid)

                return tracks

        return await asyncio.wait_for(
            asyncio.to_thread(search_related),
            timeout=timeout,
        )

    except Exception:
        return []


# ============================================================
# YouTube API-compatible class used by the rest of ShrutixMusic
# ============================================================

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(
        self,
        link: str,
        videoid: Union[bool, str] = None
    ):
        if videoid:
            link = self.base + link

        return bool(re.search(self.regex, str(link)))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]

        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)

        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption or ""
                        return text[
                            entity.offset:
                            entity.offset + entity.length
                        ]

            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url

        return None

    async def details(
        self,
        link: str,
        videoid: Union[bool, str] = None
    ):
        if videoid:
            link = self.base + link

        link = _clean_youtube_url(link)

        results = VideosSearch(link, limit=1)
        data = (await results.next()).get("result", [])

        if not data:
            raise ValueError("No YouTube result found.")

        result = data[0]

        title = result["title"]
        duration_min = result.get("duration")
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        vidid = result["id"]

        duration_sec = (
            int(time_to_seconds(duration_min))
            if duration_min else 0
        )

        return (
            title,
            duration_min,
            duration_sec,
            thumbnail,
            vidid,
        )

    async def title(
        self,
        link: str,
        videoid: Union[bool, str] = None
    ):
        details = await self.details(link, videoid)
        return details[0]

    async def duration(
        self,
        link: str,
        videoid: Union[bool, str] = None
    ):
        details = await self.details(link, videoid)
        return details[1]

    async def thumbnail(
        self,
        link: str,
        videoid: Union[bool, str] = None
    ):
        details = await self.details(link, videoid)
        return details[3]

    async def video(
        self,
        link: str,
        videoid: Union[bool, str] = None
    ):
        if videoid:
            link = self.base + link

        try:
            downloaded_file = await download_video(link)

            if downloaded_file:
                return 1, downloaded_file

            return 0, "Video download failed"

        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(
        self,
        link,
        limit,
        user_id,
        videoid: Union[bool, str] = None
    ):
        del user_id

        if videoid:
            link = self.listbase + link

        if "&" in link:
            link = link.split("&")[0]

        try:
            plist = await Playlist.get(link)
        except Exception:
            return []

        videos = plist.get("videos") or []
        ids = []

        for data in videos[:limit]:
            if not data:
                continue

            vid = data.get("id")
            if vid:
                ids.append(vid)

        return ids

    async def track(
        self,
        link: str,
        videoid: Union[bool, str] = None
    ):
        if videoid:
            link = self.base + link

        link = _clean_youtube_url(link)

        results = VideosSearch(link, limit=1)
        data = (await results.next()).get("result", [])

        if not data:
            raise ValueError("No YouTube result found.")

        result = data[0]

        title = result["title"]
        duration_min = result.get("duration")
        vidid = result["id"]
        yturl = result["link"]
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]

        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }

        return track_details, vidid

    async def formats(
        self,
        link: str,
        videoid: Union[bool, str] = None
    ):
        if videoid:
            link = self.base + link

        link = _clean_youtube_url(link)

        ytdl_opts = {
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "skip_download": True,
            "noplaylist": True,
        }

        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                r = ydl.extract_info(link, download=False)

            formats_available = []

            for fmt in r.get("formats", []):
                try:
                    if "dash" not in str(fmt.get("format", "")).lower():
                        formats_available.append(
                            {
                                "format": fmt.get("format"),
                                "filesize": fmt.get("filesize"),
                                "format_id": fmt.get("format_id"),
                                "ext": fmt.get("ext"),
                                "format_note": fmt.get("format_note"),
                                "yturl": link,
                            }
                        )
                except Exception:
                    continue

            return formats_available, link

        except Exception:
            return [], link

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None
    ):
        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result") or []

        if not result:
            raise ValueError("No YouTube results found.")

        if query_type < 0 or query_type >= len(result):
            raise IndexError("Invalid YouTube result index.")

        item = result[query_type]

        title = item["title"]
        duration_min = item.get("duration")
        vidid = item["id"]
        thumbnail = item["thumbnails"][0]["url"].split("?")[0]

        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        # Kept compatible with the original ShrutixMusic callers.
        del mystic, songaudio, songvideo, format_id, title

        if videoid:
            link = self.base + link

        try:
            if video:
                downloaded_file = await download_video(link)
            else:
                downloaded_file = await download_song(link)

            if downloaded_file:
                return downloaded_file, True

            return None, False

        except Exception:
            return None, False


YouTube = YouTubeAPI()
