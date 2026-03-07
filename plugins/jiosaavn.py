# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}splay <song name>`
    Play audio from JioSaavn in Voice Chat.
"""

import os
from pyUltroid.fns.helper import async_searcher, fast_download
from telethon.tl.types import DocumentAttributeAudio
from . import ultroid_cmd, get_string, LOGS, eor, udB

@ultroid_cmd(
    pattern="splay( (.*)|$)",
)
async def jiosaavn_play(event):
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
        song_id = song_data["id"]
        artist = song_data.get("primaryArtists") or song_data.get("artists", {}).get("primary", [{}])[0].get("name") or "Unknown Artist"
        duration = song_data.get("duration", 0)
        image_url = song_data["image"][-1]["url"] if isinstance(song_data["image"], list) and song_data["image"] else ""
        
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

        await xx.edit(f"`Playing '{title}' by {artist} from JioSaavn...`")

        # 4. Play via VCBot using the local file
        try:
            from . import vcClient
            if not vcClient:
                if os.path.exists(file_path):
                    os.remove(file_path)
                return await xx.edit(get_string("help_12"))

            import sys
            if 'vcbot' in sys.modules:
                import vcbot
                if hasattr(vcbot, 'ultSongs'):
                    # Use the local file_path instead of the URL
                    await vcbot.ultSongs.group_call.start_audio(file_path)
                    # We should probably keep the file while playing, 
                    # but many VC bots handle cleanup or need it.
                    # For now, we'll just notify success.
                    return await xx.edit(f"**Playing from JioSaavn (Local)**\n\n**Song:** `{title}`\n**Artist:** `{artist}`")

            # Fallback if VCBot objects aren't directly reachable
            return await xx.edit(f"**Song Downloaded!**\n\n**Title:** `{title}`\n**Artist:** `{artist}`\n\n`Path: {file_path}`\n`VCBot integration pending - please ensure VCBot is correctly installed.`")

        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            LOGS.exception(e)
            await xx.edit(f"`Error starting playback: {e}`")

    except Exception as e:
        LOGS.exception(e)
        await xx.edit(f"`Error: {e}`")
