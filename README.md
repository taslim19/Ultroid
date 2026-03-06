---
Ultroid Userbot
================

This is a forked / fixed version of the **Ultroid** userbot, prepared to be pushed to `https://github.com/taslim19/Ultroid`.  
It includes the core Ultroid codebase plus configuration to use the new VcBot repo at `https://github.com/taslim19/VcBot`.

### Requirements

- **Python 3.9+**
- A Telegram account and API credentials (API ID & API Hash)
- A database URL (MongoDB / Redis, as configured in `pyUltroid/configs.py`)
- Recommended: a virtual environment

Install Python dependencies with:

```bash
pip install -r requirements.txt
```

### Basic setup

1. Copy `.env.sample` to `.env` and fill in all required values (Telegram API, DB, tokens, etc.).
2. (Optional) Install local-only extras from `resources/startup/optional-requirements.txt`:

```bash
pip install -r resources/startup/optional-requirements.txt
```

3. Run the startup script:

```bash
python -m pyUltroid
```

Follow the on-screen instructions to complete session generation and bring the userbot online.

### Voice Chat Bot (VcBot)

When `VCBOT` is enabled in the database or environment, Ultroid will:

- Clone the VcBot repo from `https://github.com/taslim19/VcBot` into the `vcbot` directory (if not already present).
- Keep it updated via `git pull` on startup.

Make sure `pytgcalls` and other VcBot requirements are installed in your environment if you plan to use voice chat features.

### Notes

- Sensitive credentials (such as Google Drive OAuth client ID/secret) **must not** be hardcoded in the source files.  
  Configure them via the database keys like `GDRIVE_CLIENT_ID` and `GDRIVE_CLIENT_SECRET` instead.

For more details, browse the source in `pyUltroid/`, `plugins/`, and `assistant/`.