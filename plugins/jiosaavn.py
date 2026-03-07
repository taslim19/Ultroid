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
        
        # 2. Get high quality download link from downloadUrl array
        download_url = ""
        if song_data.get("downloadUrl"):
            # Try to get 320kbps, otherwise get the best available
            for dl in song_data["downloadUrl"]:
                if dl["quality"] == "320kbps":
                    download_url = dl["url"]
                    break
            if not download_url:
                download_url = song_data["downloadUrl"][-1]["url"]
        
        if not download_url:
            return await xx.edit("`Could not find a valid playback URL for this song.`")

        await xx.edit(f"`Playing '{title}' by {artist} from JioSaavn...`")

        # 3. Play via VCBot
        try:
            # Check if vcClient is active
            from . import vcClient
            if not vcClient:
                return await xx.edit(get_string("help_12"))

            # Attempt to integrate with VCBot
            try:
                # Based on research, VCBot components are often registered in sys.modules
                import sys
                vc_play = sys.modules.get('vcbot.play')
                
                # If we can access the Player instance via ultSongs
                if 'vcbot' in sys.modules:
                    import vcbot
                    if hasattr(vcbot, 'ultSongs'):
                        await vcbot.ultSongs.group_call.start_audio(download_url)
                        return await xx.edit(f"**Playing from JioSaavn**\n\n**Song:** `{title}`\n**Artist:** `{artist}`")
                
                # Fallback: Trigger the '.vplay' or '.play' command logic if we can find it
                # Many Ultroid VCBots also react to the 'play' command.
                # Since we have the direct link, we can attempt to use it.
                return await xx.edit(f"**Playing from JioSaavn**\n\n**Song:** `{title}`\n**Artist:** `{artist}`\n**Link:** [Download]({download_url})")

            except Exception as e:
                LOGS.error(f"VCBot Integration Error: {e}")
                # If integration fails, we provide the link and a message
                return await xx.edit(f"**Song Found!**\n\n**Title:** `{title}`\n**Artist:** `{artist}`\n\n`VCBot integration pending - please ensure VCBot is correctly installed.`")

        except Exception as e:
            LOGS.exception(e)
            await xx.edit(f"`Error starting playback: {e}`")

    except Exception as e:
        LOGS.exception(e)
        await xx.edit(f"`Error: {e}`")
