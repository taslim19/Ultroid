# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}splay <song name>`
    Play audio from JioSaavn in Voice Chat (Direct).
"""

import os
import asyncio
from pyUltroid.fns.helper import async_searcher, fast_download
from telethon.tl.types import DocumentAttributeAudio
from . import ultroid_cmd, get_string, LOGS, eor, udB, vcClient

# py-tgcalls 2.x imports
try:
    from pytgcalls import PyTgCalls
    from pytgcalls.types import AudioPiped
except ImportError:
    PyTgCalls = None
    AudioPiped = None

# Global PyTgCalls instance for this plugin
_call = None

async def get_call_client():
    global _call
    if not PyTgCalls:
        return None
    if _call is None:
        _call = PyTgCalls(vcClient)
    
    # In py-tgcalls 2.x, we can attempt to start it. 
    # If it's already started, it usually handles it or we can check status.
    try:
        await _call.start()
    except Exception:
        pass
    return _call

@ultroid_cmd(
    pattern="splay( (.*)|$)",
)
async def jiosaavn_play(event):
    if not PyTgCalls:
        return await event.eor("`'py-tgcalls' is not installed! Please install it to use this command.`", time=5)
    
    query = event.pattern_match.group(1).strip()
    if not query:
        return await event.eor("`Give me a song name to play!`", time=5)
    
    xx = await event.eor(f"`Searching for '{query}' on JioSaavn...`")
    
    # 1. Search for the song
    search_url = f"https://saavn.sumit.co/api/search/songs?query={query.replace(' ', '%20')}"
    try:
        data = await async_searcher(search_url, re_json=True)
        if not data or not data.get("data") or not data["data"].get("results"):
            return await xx.edit(f"`No results found for '{query}' on JioSaavn.`")
        
        song_data = data["data"]["results"][0]
        title = song_data["name"]
        artist = song_data.get("primaryArtists") or song_data.get("artists", {}).get("primary", [{}])[0].get("name") or "Unknown Artist"
        
        # 2. Get high quality download link
        download_url = ""
        if song_data.get("downloadUrl"):
            for dl in song_data["downloadUrl"]:
                if dl["quality"] == "320kbps":
                    download_url = dl["url"]
                    break
            if not download_url:
                download_url = song_data["downloadUrl"][-1]["url"]
        
        if not download_url:
            return await xx.edit("`Could not find a valid playback URL for this song.`")

        # 3. Download the song locally
        await xx.edit(f"`Downloading '{title}'...`")
        file_path, _ = await fast_download(download_url, filename=f"{title}.mp3")
        
        if not os.path.exists(file_path):
            return await xx.edit("`Failed to download the song for playback.`")

        await xx.edit(f"`Joining Voice Chat and playing '{title}'...`")

        # 4. Play via PyTgCalls directly
        try:
            call = await get_call_client()
            if not call:
                if os.path.exists(file_path):
                    os.remove(file_path)
                return await xx.edit("`Failed to initialize VC Client.`")

            # Play the local file
            await call.play(event.chat_id, AudioPiped(file_path))
            
            await xx.edit(f"**Playing from JioSaavn**\n\n**Song:** `{title}`\n**Artist:** `{artist}`\n**Status:** `Streaming Local File`")
            
            # Optional: We could start a background task to delete the file after some time or when playback ends.
            # But pytgcalls 2.x might need the file open. 
            # Usually, it's safer to cleanup after some delay or on stop.
            
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            LOGS.exception(e)
            await xx.edit(f"`Error starting playback: {e}`")

    except Exception as e:
        LOGS.exception(e)
        await xx.edit(f"`Error: {e}`")
