"""Text Jarvis from the phone: an iMessage to yourself becomes a turn, as if you'd said it into the mic.

The inbound half of push.py. Three rules:
  who      only the 1:1 thread with the handle in ~/.config/cbrain/imessage-to (your own number or Apple ID), so only
           your own devices can write into it. Every other chat is never read. Lines starting "Jarvis:" are the Mac's
           own pings landing in the same thread and are skipped.
  what     the text goes to the talking console like a transcript; the reply is said on the Mac as usual. A voice
           message (or any audio file) is transcribed on the Mac first (Whisper, as the mic), then goes the same way.
  back     the phone gets an ack only ("got it", then "done" or "failed"). Never the answer: employer content
           doesn't leave the Mac (your call, 2026-10-27; reconfirmed 2026-10-29).
Needs Full Disk Access for the server's Python (System Settings → Privacy & Security → Full Disk Access) to read
~/Library/Messages/chat.db. Without it the watcher logs one line and stays off.
Test: uv run webapp/inbox.py test   (prints the last messages it would see in your thread)
"""
import sqlite3
import sys
import threading
import time
from pathlib import Path

import push

DB = Path.home() / "Library" / "Messages" / "chat.db"
POLL_S = 3
DUP_S = 15     # a text to yourself can land twice (sent copy and received copy)
AUDIO = {".caf", ".m4a", ".mp3", ".wav", ".aac", ".amr", ".opus", ".aiff"}
WAIT_S = 120   # an attachment row can land before its file has downloaded
QUERY = """SELECT m.ROWID, m.text, m.attributedBody, a.filename, a.mime_type FROM message m
           JOIN chat_message_join j ON j.message_id = m.ROWID JOIN chat c ON c.ROWID = j.chat_id
           LEFT JOIN message_attachment_join maj ON maj.message_id = m.ROWID
           LEFT JOIN attachment a ON a.ROWID = maj.attachment_id
           WHERE c.chat_identifier = ? AND c.style = 45 AND m.ROWID > ? AND m.item_type = 0
           ORDER BY m.ROWID"""


def body(text, blob):
    """The message text. Newer macOS leaves `text` empty and keeps it in the attributedBody typedstream."""
    if text:
        return text
    i = (blob or b"").find(b"NSString")
    if i < 0:
        return ""
    b = blob[i + 13:]                     # "NSString" + 5 bytes of class/type header, then the length
    n, b = b[0], b[1:]
    if n == 0x81:
        n, b = int.from_bytes(b[:2], "little"), b[2:]
    elif n == 0x82:
        n, b = int.from_bytes(b[:3], "little"), b[3:]
    return b[:n].decode("utf-8", "ignore")


def audio(filename, mime):
    if not filename:
        return None
    f = Path(filename).expanduser()
    return f if f.suffix.lower() in AUDIO or (mime or "").startswith("audio/") else None


def rows(after):
    """(rowid, text, audio path or None). U+FFFC is the attachment's placeholder in the text, not something you typed."""
    with sqlite3.connect(f"file:{DB}?mode=ro", uri=True) as db:
        return [(r, body(t, a).replace("\ufffc", "").strip(), audio(f, mt))
                for r, t, a, f, mt in db.execute(QUERY, (push.handle(), after))]


def watch(on_text, on_audio):
    """Calls on_text(text) or on_audio(path) for each new message you send yourself. Starts after what's already there."""
    if not push.handle():
        return print(f"inbox: off (no handle in {push.HANDLE_F})", flush=True)
    try:
        with sqlite3.connect(f"file:{DB}?mode=ro", uri=True) as db:
            last = db.execute("SELECT IFNULL(MAX(ROWID), 0) FROM message").fetchone()[0]
    except sqlite3.Error as e:
        return print(f"inbox: off ({e}; give the server's Python Full Disk Access)", flush=True)

    def loop():
        nonlocal last
        seen, waiting = {}, {}      # waiting: audio path -> give-up time, until its file has downloaded
        while True:
            time.sleep(POLL_S)
            try:
                new = rows(last)
            except sqlite3.Error as e:
                print(f"inbox: {e}", flush=True)
                continue
            for rowid, text, f in new:
                last = rowid
                if f:
                    waiting.setdefault(f, time.time() + WAIT_S)
                elif text and not text.startswith("Jarvis:") and time.time() - seen.get(text, 0) >= DUP_S:
                    seen[text] = time.time()
                    on_text(text)
            for f, until in list(waiting.items()):
                if f.exists() and f.stat().st_size:
                    del waiting[f]
                    key = f"audio:{f.name}:{f.stat().st_size}"
                    if time.time() - seen.get(key, 0) >= DUP_S:
                        seen[key] = time.time()
                        on_audio(f)
                elif time.time() > until:
                    del waiting[f]
                    print(f"inbox: gave up waiting for {f.name}", flush=True)

    threading.Thread(target=loop, daemon=True).start()
    print(f"inbox: watching your thread with {push.handle()}", flush=True)


if __name__ == "__main__" and sys.argv[1:] == ["test"]:
    if not push.handle():
        sys.exit(f"no handle: put your phone number or Apple ID in {push.HANDLE_F}")
    for rowid, text, f in rows(0)[-5:]:
        print(rowid, repr(text), f or "")
