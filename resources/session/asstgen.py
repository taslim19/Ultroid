#!/usr/bin/env python3

import os
from time import sleep

try:
    from telethon import TelegramClient
except ImportError:
    print("Installing telethon...")
    os.system("pip install telethon")
    from telethon import TelegramClient

def clear_screen():
    if os.name == "posix":
        os.system("clear")
    else:
        os.system("cls")

clear_screen()
print("\n--- Assistant Session Generator ---\n")

try:
    API_ID = int(input("Enter your API ID: "))
    API_HASH = input("Enter your API HASH: ")
    BOT_TOKEN = input("Enter your BOT TOKEN: ")

    print("\nStarting Telethon client and generating session...")
    
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    session_path = os.path.join(root_dir, 'asst')

    bot = TelegramClient(session_path, API_ID, API_HASH)
    bot.start(bot_token=BOT_TOKEN)
    bot.disconnect()

    # The journal file gets automatically cleaned up by sqlite3 when disconnect() is called
    # By creating a copy of the saved session explicitly after disconnection, 
    # we ensure the user has the -journal file they need for their specific deployment.
    import shutil
    if os.path.exists(f'{session_path}.session'):
        shutil.copy2(f'{session_path}.session', f'{session_path}.session-journal')

    print("\n✅ Success!")
    print(f"The files 'asst.session' and 'asst.session-journal' are now available in your root folder: {root_dir}")


except ValueError:
    print("\n[ERROR] API ID must be a number! Please try again.")
except Exception as e:
    print(f"\n[ERROR] An unexpected error occurred: {e}")
