# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}splay <song name>`
    Play audio from JioSaavn in Voice Chat.
• `{i}pause`
    Pause the current playback.
• `{i}resume`
    Resume the paused playback.
• `{i}skip`
    Skip the current song.
• `{i}queue`
    Show the current song queue.
• `{i}end`
    Stop playback and leave Voice Chat.
"""

import os
import asyncio
from pyUltroid.fns.helper import async_searcher, fast_download
from telethon import TelegramClient
from . import ultroid_cmd, LOGS, eor, udB

# py-tgcalls 2.x imports (v2.2.11 compatible)
try:
    from pytgcalls import PyTgCalls
    from pytgcalls.types import MediaStream, AudioQuality, Update
    from pytgcalls.types.stream import StreamDeleted
except Exception as e:
    LOGS.error(f"py-tgcalls 2.x import failed: {e}")
    PyTgCalls = None
    MediaStream = None
    AudioQuality = None

# Global state
_call = None
SONG_QUEUE = {}  # {chat_id: [{"title": T, "artist": A, "url": U, "thumb": Th}, ...]}
CURRENT_SONG = {} # {chat_id: {"title": T, ...}}

async def get_call_client(client):
    global _call
    if not PyTgCalls:
        return None
    if _call is None:
        try:
            original_class = client.__class__
            client.__class__ = TelegramClient
            try:
                _call = PyTgCalls(client)
                
                @_call.on_update()
                async def update_handler(client, update):
                    if isinstance(update, StreamDeleted):
                        await play_next(update.chat_id, client)

                LOGS.info("JioSaavn Playback: PyTgCalls initialized.")
            finally:
                client.__class__ = original_class
        except Exception as e:
            LOGS.error(f"PyTgCalls init failed: {e}")
            return None
    
    try:
        if not getattr(_call, 'is_running', False):
            await _call.start()
    except Exception:
        pass
    return _call

async def play_next(chat_id, client=None):
    if chat_id not in SONG_QUEUE or not SONG_QUEUE[chat_id]:
        CURRENT_SONG.pop(chat_id, None)
        try:
            await _call.leave_call(chat_id)
        except:
            pass
        return

    song = SONG_QUEUE[chat_id].pop(0)
    CURRENT_SONG[chat_id] = song
    
    title = song["title"]
    download_url = song["url"]
    image_url = song["thumb"]
    
    # Download
    file_path, _ = await fast_download(download_url, filename=f"{title}.mp3")
    
    if not os.path.exists(file_path):
        LOGS.error(f"Failed to download {title} for queue playback.")
        return await play_next(chat_id, client)
    
    try:
        await _call.play(chat_id, MediaStream(file_path, AudioQuality.STUDIO))
    except Exception as e:
        LOGS.error(f"Error playing {title} from queue: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        await play_next(chat_id, client)

@ultroid_cmd(pattern="splay( (.*)|$)")
async def jiosaavn_play(event):
    if not PyTgCalls:
        return await event.eor("`'py-tgcalls' is missing!`", time=5)
    
    query = event.pattern_match.group(1).strip()
    if not query:
        return await event.eor("`Give me a song name!`", time=5)
    
    xx = await event.eor(f"`Searching for '{query}'...`")
    search_url = f"https://saavn.sumit.co/api/search/songs?query={query.replace(' ', '%20')}"
    
    try:
        data = await async_searcher(search_url, re_json=True)
        if not data or not data.get("data") or not data["data"].get("results"):
            return await xx.edit(f"`No results for '{query}'.`")
        
        song_data = data["data"]["results"][0]
        title = song_data["name"]
        artist = song_data.get("primaryArtists") or "Unknown"
        image_url = song_data.get("image", [{}])[-1].get("url") if song_data.get("image") else ""
        
        download_url = ""
        if song_data.get("downloadUrl"):
            for dl in song_data["downloadUrl"]:
                if dl["quality"] == "320kbps":
                    download_url = dl["url"]
                    break
            if not download_url:
                download_url = song_data["downloadUrl"][-1]["url"]
        
        if not download_url:
            return await xx.edit("`No valid URL found.`")

        song_info = {
            "title": title,
            "artist": artist,
            "url": download_url,
            "thumb": image_url
        }

        call = await get_call_client(event.client)
        if not call:
            return await xx.edit("`FC Client Error.`")

        # Check if already playing
        if event.chat_id in CURRENT_SONG:
            if event.chat_id not in SONG_QUEUE:
                SONG_QUEUE[event.chat_id] = []
            SONG_QUEUE[event.chat_id].append(song_info)
            return await xx.edit(f"**Added to Queue**\n\n**Song:** `{title}`\n**Position:** `{len(SONG_QUEUE[event.chat_id])}`")

        # Not playing, start now
        await xx.edit(f"`Downloading '{title}'...`")
        file_path, _ = await fast_download(download_url, filename=f"{title}.mp3")
        
        if not os.path.exists(file_path):
            return await xx.edit("`Download failed.`")

        await xx.edit(f"`Playing '{title}'...`")
        try:
            CURRENT_SONG[event.chat_id] = song_info
            await call.play(event.chat_id, MediaStream(file_path, AudioQuality.STUDIO))
            thumb = f"[\u200c]({image_url})" if image_url else ""
            await xx.edit(f"{thumb}**Playing from JioSaavn**\n\n**Song:** `{title}`\n**Artist:** `{artist}`\n**Status:** `Streaming`")
        except Exception as e:
            CURRENT_SONG.pop(event.chat_id, None)
            if os.path.exists(file_path): os.remove(file_path)
            await xx.edit(f"`Error: {e}`")

    except Exception as e:
        LOGS.exception(e)
        await xx.edit(f"`Error: {e}`")

@ultroid_cmd(pattern="pause$")
async def pause_play(event):
    call = await get_call_client(event.client)
    if not call: return
    try:
        await call.pause_stream(event.chat_id)
        await event.eor("`Paused playback.`", time=5)
    except Exception as e:
        await event.eor(f"`Error: {e}`", time=5)

@ultroid_cmd(pattern="resume$")
async def resume_play(event):
    call = await get_call_client(event.client)
    if not call: return
    try:
        await call.resume_stream(event.chat_id)
        await event.eor("`Resumed playback.`", time=5)
    except Exception as e:
        await event.eor(f"`Error: {e}`", time=5)

@ultroid_cmd(pattern="skip$")
async def skip_play(event):
    if event.chat_id not in CURRENT_SONG:
        return await event.eor("`Nothing is playing!`", time=5)
    await event.eor("`Skipping current song...`", time=5)
    await play_next(event.chat_id, event.client)

@ultroid_cmd(pattern="end$")
async def end_play(event):
    call = await get_call_client(event.client)
    if not call: return
    try:
        SONG_QUEUE.pop(event.chat_id, None)
        CURRENT_SONG.pop(event.chat_id, None)
        await call.leave_call(event.chat_id)
        await event.eor("`Stopped playback and cleared queue.`", time=5)
    except Exception as e:
        await event.eor(f"`Error: {e}`", time=5)

@ultroid_cmd(pattern="queue$")
async def show_queue(event):
    if event.chat_id not in SONG_QUEUE or not SONG_QUEUE[event.chat_id]:
        if event.chat_id in CURRENT_SONG:
            return await event.eor(f"**Now Playing:** `{CURRENT_SONG[event.chat_id]['title']}`\n\n**Queue is empty.**")
        return await event.eor("`Queue is empty.`")
    
    msg = f"**Now Playing:** `{CURRENT_SONG[event.chat_id]['title']}`\n\n**Upcoming:**\n"
    for i, song in enumerate(SONG_QUEUE[event.chat_id], 1):
        msg += f"{i}. `{song['title']}`\n"
    await event.eor(msg)
